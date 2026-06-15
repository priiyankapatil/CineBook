import os
import pickle
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from flask import current_app
from sqlalchemy import func

MOVIELENS_DIR = None
MODEL_DIR = None
_model_cache = None


def _get_paths():
    global MOVIELENS_DIR, MODEL_DIR
    if MOVIELENS_DIR is None:
        MOVIELENS_DIR = current_app.config['MOVIELENS_DIR']
        MODEL_DIR = current_app.config['MODEL_DIR']


def _load_movielens():
    _get_paths()
    ratings = pd.read_csv(os.path.join(MOVIELENS_DIR, 'ratings.csv'))
    movies = pd.read_csv(os.path.join(MOVIELENS_DIR, 'movies.csv'))
    return ratings, movies


def _build_user_item_matrix(ratings):
    pivot = ratings.pivot_table(
        index='userId', columns='movieId', values='rating'
    ).fillna(0)
    sparse_matrix = csr_matrix(pivot.values)
    return sparse_matrix, list(pivot.index), list(pivot.columns)


def train():
    _get_paths()
    ratings, movies = _load_movielens()
    sparse_matrix, user_ids, movie_ids = _build_user_item_matrix(ratings)

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(os.path.join(MODEL_DIR, 'recommender_model.pkl'), 'wb') as f:
        pickle.dump({
            'user_item_matrix': sparse_matrix,
            'user_ids': user_ids,
            'movie_ids': movie_ids,
        }, f)

    movies.to_pickle(os.path.join(MODEL_DIR, 'movielens_movies.pkl'))
    print(f'Model trained: {len(user_ids)} users, {len(movie_ids)} movies')


def _load_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    _get_paths()
    model_path = os.path.join(MODEL_DIR, 'recommender_model.pkl')
    if not os.path.exists(model_path):
        return None
    with open(model_path, 'rb') as f:
        _model_cache = pickle.load(f)
    return _model_cache


def _get_user_genre_prefs(app_user_id):
    from app.models import Review, Movie
    reviews = Review.query.filter_by(user_id=app_user_id).all()
    if not reviews:
        return {}

    genre_scores = {}
    for review in reviews:
        movie = Movie.query.get(review.movie_id)
        if movie and movie.genre:
            genres = [g.strip() for g in movie.genre.split(',')]
            for genre in genres:
                genre_scores[genre] = genre_scores.get(genre, 0) + review.rating

    total = sum(genre_scores.values())
    if total == 0:
        return {}
    return {g: round(s / total, 3) for g, s in genre_scores.items()}


def recommend_for_app_user(app_user_id, n=5):
    from app.models import Review, Movie, Booking, SearchLog
    from app.extensions import db

    # ---- Gather all user signals ----
    # Booked movies (positive intent signal)
    booked_movie_ids = set()
    bookings = Booking.query.filter_by(user_id=app_user_id, status='confirmed').all()
    for b in bookings:
        booked_movie_ids.add(b.show.movie_id)

    # Reviewed movies (with rating)
    reviewed_movie_ids = set()
    reviews = Review.query.filter_by(user_id=app_user_id).all()
    for r in reviews:
        reviewed_movie_ids.add(r.movie_id)

    # Get user's genre preferences from reviews + bookings
    genre_prefs = _get_user_genre_prefs(app_user_id)
    if not genre_prefs and booked_movie_ids:
        booked_movies = Movie.query.filter(Movie.id.in_(booked_movie_ids)).all()
        genre_scores = {}
        for m in booked_movies:
            if m.genre:
                for g in m.genre.split(','):
                    g = g.strip()
                    genre_scores[g] = genre_scores.get(g, 0) + 1
        total = sum(genre_scores.values())
        if total > 0:
            genre_prefs = {g: round(s / total, 3) for g, s in genre_scores.items()}

    # If still no preferences, try search history
    if not genre_prefs:
        searches = SearchLog.query.filter_by(user_id=app_user_id).order_by(SearchLog.created_at.desc()).limit(20).all()
        search_terms = [s.search_query.lower() for s in searches]
        if search_terms:
            all_movies = Movie.query.all()
            genre_hits = {}
            for m in all_movies:
                if m.title.lower() in ' '.join(search_terms):
                    if m.genre:
                        for g in m.genre.split(','):
                            g = g.strip()
                            genre_hits[g] = genre_hits.get(g, 0) + 1
            total = sum(genre_hits.values())
            if total > 0:
                genre_prefs = {g: round(s / total, 3) for g, s in genre_hits.items()}

    # ---- Score local movies ----
    all_local = Movie.query.all()
    scored = []

    for movie in all_local:
        if movie.id in reviewed_movie_ids:
            continue

        score = 0.0

        # Signal 1: booked → strong positive
        if movie.id in booked_movie_ids:
            score += 2.0

        # Signal 2: review rating → if they reviewed it (already filtered above), skip
        # But if they gave a high rating in a review, we might want to boost similar movies

        # Signal 3: genre match → boost based on preferences
        if genre_prefs and movie.genre:
            movie_genres = [g.strip() for g in movie.genre.split(',')]
            for mg in movie_genres:
                for gp, gw in genre_prefs.items():
                    if mg.lower() == gp.lower():
                        score += gw * 1.5  # genre boost

        # Signal 4: MovieLens collaborative filtering (bonus)
        model = _load_model()
        if model and movie.mlens_movie_id:
            mlens_mid = movie.mlens_movie_id
            movie_ids_ls = model['movie_ids']
            user_ids_ls = model['user_ids']
            user_item_matrix = model['user_item_matrix']
            movie_id_to_idx = {mid: i for i, mid in enumerate(movie_ids_ls)}
            user_id_to_idx = {uid: i for i, uid in enumerate(user_ids_ls)}

            if mlens_mid in movie_id_to_idx:
                mv_idx = movie_id_to_idx[mlens_mid]
                mv_vector = user_item_matrix[:, mv_idx].toarray().flatten()
                avg_ml_rating = mv_vector[mv_vector > 0].mean() if mv_vector.sum() > 0 else 0
                # Weighted by how many ML users rated it
                rating_count = (mv_vector > 0).sum()
                if avg_ml_rating > 0:
                    ml_score = (avg_ml_rating / 5.0) * min(rating_count / 100, 1.0)
                    score += ml_score * 0.5

        scored.append({
            'movie': movie,
            'score': round(score, 3),
        })

    scored.sort(key=lambda x: x['score'], reverse=True)

    result = []
    for item in scored[:n]:
        result.append({
            'local_id': item['movie'].id,
            'title': item['movie'].title,
            'poster_url': item['movie'].poster_url,
            'genre': item['movie'].genre,
            'score': item['score'],
        })

    return result


def _load_movies_meta():
    _get_paths()
    path = os.path.join(MODEL_DIR, 'movielens_movies.pkl')
    if os.path.exists(path):
        return pd.read_pickle(path)
    return None
