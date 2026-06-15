import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')

    _db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL') or ''
    if _db_url and _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///' + os.path.join(basedir, 'data', 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MOVIELENS_DIR = os.path.join(basedir, 'data', 'ml-latest-small')
    MODEL_DIR = os.path.join(basedir, 'data', 'models')
