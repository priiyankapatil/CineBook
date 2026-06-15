from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Movie, Show, Review, SearchLog
from app.extensions import db
from app.ml.recommender import recommend_for_app_user

movies_bp = Blueprint('movies', __name__)


@movies_bp.route('/')
def index():
    genre_filter = request.args.get('genre')
    search_query = request.args.get('q', '').strip()
    query = Movie.query

    if genre_filter:
        query = query.filter(Movie.genre.ilike(f'%{genre_filter}%'))

    if search_query:
        query = query.filter(
            Movie.title.ilike(f'%{search_query}%') |
            Movie.director.ilike(f'%{search_query}%') |
            Movie.genre.ilike(f'%{search_query}%')
        )
        if current_user.is_authenticated:
            db.session.add(SearchLog(user_id=current_user.id, search_query=search_query))
            db.session.commit()

    movies = query.order_by(Movie.title).all()
    genres = ['Action', 'Comedy', 'Crime', 'Drama', 'Sci-Fi', 'Thriller', 'Animation']

    recommendations = []
    if current_user.is_authenticated:
        recommendations = recommend_for_app_user(current_user.id, n=5)

    return render_template('index.html', movies=movies, genres=genres,
                           selected_genre=genre_filter, search_query=search_query,
                           recommendations=recommendations)


@movies_bp.route('/movies/<int:movie_id>')
def detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    shows = Show.query.filter_by(movie_id=movie_id).order_by(Show.show_time).all()
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).all()

    shows_by_theatre = {}
    for show in shows:
        theatre_name = show.theatre.name
        if theatre_name not in shows_by_theatre:
            shows_by_theatre[theatre_name] = {
                'location': show.theatre.location,
                'shows': [],
            }
        shows_by_theatre[theatre_name]['shows'].append(show)

    sentiment_summary = {'positive': 0, 'neutral': 0, 'negative': 0}
    for r in reviews:
        if r.sentiment_score is not None:
            if r.sentiment_score > 0.1:
                sentiment_summary['positive'] += 1
            elif r.sentiment_score < -0.1:
                sentiment_summary['negative'] += 1
            else:
                sentiment_summary['neutral'] += 1

    return render_template('movie_detail.html', movie=movie,
                           shows_by_theatre=shows_by_theatre,
                           reviews=reviews,
                           sentiment_summary=sentiment_summary)


@movies_bp.route('/api/recommendations')
@login_required
def api_recommendations():
    recs = recommend_for_app_user(current_user.id, n=5)
    return jsonify(recs)
