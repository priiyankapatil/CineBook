from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Review, Movie
from app.ml.sentiment import analyze_sentiment

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/<int:movie_id>', methods=['POST'])
@login_required
def submit_review(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    rating = int(request.form['rating'])
    review_text = request.form.get('review_text', '').strip()

    if rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5.', 'danger')
        return redirect(url_for('movies.detail', movie_id=movie_id))

    if Review.query.filter_by(user_id=current_user.id,
                               movie_id=movie_id).first():
        flash('You have already reviewed this movie.', 'warning')
        return redirect(url_for('movies.detail', movie_id=movie_id))

    sentiment = None
    if review_text:
        sentiment = analyze_sentiment(review_text)

    review = Review(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=rating,
        review_text=review_text,
        sentiment_score=sentiment,
    )
    db.session.add(review)

    all_ratings = [r.rating for r in movie.reviews.all()]
    if all_ratings:
        movie.avg_rating = round(sum(all_ratings) / len(all_ratings), 1)

    db.session.commit()
    flash('Review submitted!', 'success')
    return redirect(url_for('movies.detail', movie_id=movie_id))
