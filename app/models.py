from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    genre = db.Column(db.String(200), nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=False, default=120)
    release_date = db.Column(db.Date, nullable=True)
    director = db.Column(db.String(200), nullable=True)
    language = db.Column(db.String(50), default='English')
    poster_url = db.Column(db.String(500), nullable=True)
    avg_rating = db.Column(db.Float, default=0.0)
    mlens_movie_id = db.Column(db.Integer, nullable=True)

    shows = db.relationship('Show', backref='movie', lazy='dynamic')
    reviews = db.relationship('Review', backref='movie', lazy='dynamic')

    def __repr__(self):
        return f'<Movie {self.title}>'


class Theatre(db.Model):
    __tablename__ = 'theatres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    total_screens = db.Column(db.Integer, default=1)

    screens = db.relationship('Screen', backref='theatre', lazy='dynamic')

    def __repr__(self):
        return f'<Theatre {self.name}>'


class Screen(db.Model):
    __tablename__ = 'screens'

    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'), nullable=False)
    screen_number = db.Column(db.Integer, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False, default=50)

    shows = db.relationship('Show', backref='screen', lazy='dynamic')
    seats = db.relationship('Seat', backref='screen', lazy='dynamic')

    def __repr__(self):
        return f'<Screen {self.screen_number} @ Theatre {self.theatre_id}>'


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    screen_id = db.Column(db.Integer, db.ForeignKey('screens.id'), nullable=False)
    show_time = db.Column(db.DateTime, nullable=False)
    base_price = db.Column(db.Float, nullable=False, default=10.0)

    bookings = db.relationship('Booking', backref='show', lazy='dynamic')

    @property
    def theatre(self):
        return self.screen.theatre

    def __repr__(self):
        return f'<Show {self.movie.title} @ {self.show_time}>'


class Seat(db.Model):
    __tablename__ = 'seats'

    id = db.Column(db.Integer, primary_key=True)
    screen_id = db.Column(db.Integer, db.ForeignKey('screens.id'), nullable=False)
    seat_row = db.Column(db.String(5), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    seat_type = db.Column(db.String(20), default='standard')
    price_multiplier = db.Column(db.Float, default=1.0)

    booking_seats = db.relationship('BookingSeat', backref='seat', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('screen_id', 'seat_row', 'seat_number',
                            name='uq_seat_screen_row_number'),
    )

    def __repr__(self):
        return f'<Seat {self.seat_row}{self.seat_number} ({self.seat_type})>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('shows.id'), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='confirmed')

    booking_seats = db.relationship('BookingSeat', backref='booking', lazy='dynamic',
                                    cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.id} by User {self.user_id}>'


class BookingSeat(db.Model):
    __tablename__ = 'booking_seats'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    price_at_booking = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('booking_id', 'seat_id', name='uq_booking_seat'),
    )

    def __repr__(self):
        return f'<BookingSeat Booking {self.booking_id} Seat {self.seat_id}>'


class SearchLog(db.Model):
    __tablename__ = 'search_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    search_query = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='search_logs')

    def __repr__(self):
        return f'<SearchLog User {self.user_id} q={self.search_query}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='uq_user_movie_review'),
    )

    def __repr__(self):
        return f'<Review User {self.user_id} Movie {self.movie_id} Rating {self.rating}>'
