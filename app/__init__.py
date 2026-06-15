import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.movies import movies_bp
    from app.routes.bookings import bookings_bp
    from app.routes.reviews import reviews_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(movies_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(reviews_bp, url_prefix='/review')

    with app.app_context():
        db.create_all()
        from app.models import Movie
        if Movie.query.count() == 0:
            from seed_db import seed
            seed(app)

    @app.route('/api/train')
    def train_recommender():
        from app.ml.recommender import train
        from flask import jsonify
        try:
            train()
            return jsonify({'status': 'ok', 'message': 'Recommender trained'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return app
