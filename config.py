import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'data', 'app.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MOVIELENS_DIR = os.path.join(basedir, 'data', 'ml-latest-small')
    MODEL_DIR = os.path.join(basedir, 'data', 'models')
