from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Show, Seat, Booking, BookingSeat
from app.ml.pricing import predict_seat_price

bookings_bp = Blueprint('bookings', __name__)


@bookings_bp.route('/book/<int:show_id>')
@login_required
def seat_selection(show_id):
    show = Show.query.get_or_404(show_id)
    seats = Seat.query.filter_by(screen_id=show.screen_id)\
        .order_by(Seat.seat_row, Seat.seat_number).all()

    booked_seat_ids = set()
    for booking in show.bookings:
        if booking.status == 'confirmed':
            for bs in booking.booking_seats:
                booked_seat_ids.add(bs.seat_id)

    for seat in seats:
        seat.is_booked = seat.id in booked_seat_ids
        seat.dynamic_price = predict_seat_price(show, seat)

    rows = {}
    for seat in seats:
        rows.setdefault(seat.seat_row, []).append(seat)

    return render_template('seat_selection.html', show=show, rows=rows)


@bookings_bp.route('/book/<int:show_id>/confirm', methods=['POST'])
@login_required
def confirm_booking(show_id):
    show = Show.query.get_or_404(show_id)

    if show.show_time < datetime.utcnow():
        flash('This show has already started.', 'danger')
        return redirect(url_for('movies.detail', movie_id=show.movie_id))

    seat_ids = request.form.getlist('seat_ids')
    if not seat_ids:
        flash('Please select at least one seat.', 'danger')
        return redirect(url_for('bookings.seat_selection', show_id=show_id))

    try:
        seat_ids = [int(sid) for sid in seat_ids]
    except ValueError:
        flash('Invalid seat selection.', 'danger')
        return redirect(url_for('bookings.seat_selection', show_id=show_id))

    seats = Seat.query.filter(Seat.id.in_(seat_ids)).all()

    if len(seats) != len(seat_ids):
        flash('Some seats were not found.', 'danger')
        return redirect(url_for('bookings.seat_selection', show_id=show_id))

    for seat in seats:
        for booking in show.bookings:
            if booking.status == 'confirmed':
                for bs in booking.booking_seats:
                    if bs.seat_id == seat.id:
                        flash(f'Seat {seat.seat_row}{seat.seat_number} is already booked.',
                              'danger')
                        return redirect(url_for('bookings.seat_selection',
                                                show_id=show_id))

    total = 0
    booking = Booking(user_id=current_user.id, show_id=show_id, total_amount=0)
    db.session.add(booking)
    db.session.flush()

    for seat in seats:
        price = predict_seat_price(show, seat)
        bs = BookingSeat(booking_id=booking.id, seat_id=seat.id,
                         price_at_booking=price)
        db.session.add(bs)
        total += price

    booking.total_amount = round(total, 2)
    db.session.commit()

    return redirect(url_for('bookings.confirmation', booking_id=booking.id))


@bookings_bp.route('/booking/<int:booking_id>')
@login_required
def confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash('You can only view your own bookings.', 'danger')
        return redirect(url_for('movies.index'))

    return render_template('booking_confirmation.html', booking=booking)


@bookings_bp.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id)\
        .order_by(Booking.booking_time.desc()).all()
    return render_template('my_bookings.html', bookings=bookings, utcnow=datetime.utcnow())


@bookings_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash('You can only cancel your own bookings.', 'danger')
        return redirect(url_for('movies.index'))

    if booking.status == 'cancelled':
        flash('Booking is already cancelled.', 'info')
    else:
        booking.status = 'cancelled'
        db.session.commit()
        flash('Booking cancelled successfully.', 'success')

    return redirect(url_for('bookings.my_bookings'))


@bookings_bp.route('/ticket/<int:booking_id>')
@login_required
def ticket(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash('You can only view your own tickets.', 'danger')
        return redirect(url_for('movies.index'))

    seat_list = [bs.seat for bs in booking.booking_seats]

    return render_template('ticket.html', booking=booking, seats=seat_list)
