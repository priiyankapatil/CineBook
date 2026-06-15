"""
Dynamic Seat Pricing using Regression.

How it works:
- Training: historical booking data (time_to_show, day_of_week, occupancy, etc.)
  is used to train a LinearRegression model that predicts the price premium.
- Prediction: for a given show + seat, the model predicts the optimal price.

The model is trained offline via the train() function and saved as a pickle.
If no model exists yet, it falls back to base_price * seat_type_multiplier.
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime
from flask import current_app

MODEL_DIR = None
_model_cache = None


def _get_paths():
    global MODEL_DIR
    if MODEL_DIR is None:
        MODEL_DIR = current_app.config['MODEL_DIR']


def _engineer_features(show, seat):
    """
    Create feature vector for a (show, seat) pair.
    Features used by the model during both training and prediction.
    """
    show_time = show.show_time
    now = datetime.utcnow()

    days_until_show = (show_time - now).total_seconds() / 86400.0
    hour = show_time.hour
    is_weekend = 1 if show_time.weekday() >= 5 else 0
    seat_type_encoded = {'standard': 0, 'vip': 1, 'recliner': 2}.get(seat.seat_type, 0)

    # Count how many seats are already booked for this show
    total_seats = seat.screen.total_seats
    booked_count = 0
    for booking in show.bookings:
        if booking.status == 'confirmed':
            booked_count += booking.booking_seats.count()

    occupancy_ratio = booked_count / max(total_seats, 1)

    return np.array([[
        days_until_show,
        hour,
        is_weekend,
        seat_type_encoded,
        occupancy_ratio,
        seat.price_multiplier,
    ]])


def train():
    """
    Generate synthetic training data from existing booking records
    and train the pricing regression model.
    Run this after you have some booking history.
    """
    _get_paths()
    from app.extensions import db
    from app.models import BookingSeat, Show, Seat

    records = db.session.query(BookingSeat, Show, Seat).join(
        Show, BookingSeat.seat_id == Show.id
    ).join(
        Seat, BookingSeat.seat_id == Seat.id
    ).all()

    if not records:
        print('No booking data to train on yet.')
        return

    X, y = [], []
    for bs, show, seat in records:
        if show and seat:
            features = _engineer_features(show, seat)
            X.append(features[0])
            y.append(bs.price_at_booking)

    if not X:
        print('Not enough data to train.')
        return

    X = np.array(X)
    y = np.array(y)

    model = LinearRegression()
    model.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(os.path.join(MODEL_DIR, 'pricing_model.pkl'), 'wb') as f:
        pickle.dump(model, f)

    print(f'Pricing model trained on {len(X)} samples. Score: {model.score(X, y):.3f}')


def predict_seat_price(show, seat):
    """
    Predict the optimal price for a given show and seat.
    Falls back to base_price * price_multiplier if no model exists.
    """
    _get_paths()
    global _model_cache

    model_path = os.path.join(MODEL_DIR, 'pricing_model.pkl')

    if _model_cache is None and os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            _model_cache = pickle.load(f)

    if _model_cache is not None:
        try:
            features = _engineer_features(show, seat)
            predicted = _model_cache.predict(features)[0]
            return round(max(predicted, show.base_price * 0.5), 2)
        except Exception:
            pass

    return round(show.base_price * seat.price_multiplier, 2)
