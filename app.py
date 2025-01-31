from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_, or_
from datetime import datetime

app = Flask(__name__)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///railway_tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database models
class Passenger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)
    berth_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    passengers = db.relationship('Passenger', backref='ticket', lazy=True)

class Berth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    berth_number = db.Column(db.Integer, unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)

# Create tables and insert initial data
with app.app_context():
    db.create_all()

    if Berth.query.count() == 0:
        berths_data = [
            (1, 'lower'), (2, 'lower'), (3, 'lower'), (4, 'lower'), (5, 'lower'), (6, 'lower'), (7, 'lower'), (8, 'lower'), (9, 'lower'),
            (10, 'side-lower'), (11, 'side-lower'), (12, 'side-lower'), (13, 'side-lower'), (14, 'side-lower'), (15, 'side-lower'), (16, 'side-lower'), (17, 'side-lower'), (18, 'side-lower'),
            (19, 'upper'), (20, 'upper'), (21, 'upper'), (22, 'upper'), (23, 'upper'), (24, 'upper'), (25, 'upper'), (26, 'upper'), (27, 'upper')
        ]
        for berth_number, berth_type in berths_data:
            berth = Berth(berth_number=berth_number, type=berth_type)
            db.session.add(berth)
        db.session.commit()


def get_available_berth(priority_passengers=None):
    """
    Get an available berth based on priority.
    Priority passengers (aged 60+ or ladies with children) get lower berths if available.
    """
    if priority_passengers:

        lower_berth = Berth.query.filter_by(type='lower', is_occupied=False).first()
        if lower_berth:
            return lower_berth

    return Berth.query.filter_by(is_occupied=False).first()

def update_berth_status(berth_number, is_occupied):
    berth = Berth.query.filter_by(berth_number=berth_number).first()
    if berth:
        berth.is_occupied = is_occupied
        db.session.commit()

def get_ticket_status_count(status):
    return Ticket.query.filter_by(status=status).count()

def has_priority_passengers(passengers):
    """
    Check if there are priority passengers (aged 60+ or ladies with children).
    """
    for passenger in passengers:
        if passenger['age'] >= 60:
            return True
        if passenger['gender'] == 'female' and any(p['age'] < 5 for p in passengers):
            return True
    return False


@app.route('/api/v1/tickets/book', methods=['POST'])
def book_ticket():
    data = request.get_json()
    passengers_data = data.get('passengers', [])

    # Check if waiting list is full
    waiting_count = get_ticket_status_count('waiting')
    if waiting_count >= 10:
        return jsonify({"error": "No tickets available"}), 400

    # Check for priority passengers
    priority_passengers = has_priority_passengers(passengers_data)

    # Check for available berths
    berth = get_available_berth(priority_passengers)
    if not berth:
        return jsonify({"error": "No berths available"}), 400

    # Assign berth and create ticket
    ticket_status = 'confirmed' if berth.type != 'side-lower' else 'RAC'
    ticket = Ticket(status=ticket_status, berth_number=berth.berth_number)
    db.session.add(ticket)
    db.session.commit()

    # Update berth status
    update_berth_status(berth.berth_number, True)

    # Add passengers
    for passenger_data in passengers_data:
        passenger = Passenger(
            name=passenger_data['name'],
            age=passenger_data['age'],
            gender=passenger_data['gender'],
            ticket_id=ticket.id
        )
        db.session.add(passenger)
    db.session.commit()

    return jsonify({
        "ticket_id": ticket.id,
        "status": ticket.status,
        "berth_number": ticket.berth_number,
        "passengers": passengers_data
    }), 201

@app.route('/api/v1/tickets/cancel/<int:ticket_id>', methods=['POST'])
def cancel_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    # Free the berth
    update_berth_status(ticket.berth_number, False)

    # Promote RAC to confirmed and waiting to RAC
    if ticket.status == 'confirmed':
        rac_ticket = Ticket.query.filter_by(status='RAC').first()
        if rac_ticket:
            rac_ticket.status = 'confirmed'
            update_berth_status(rac_ticket.berth_number, True)
            db.session.commit()

    # Delete ticket
    db.session.delete(ticket)
    db.session.commit()

    return jsonify({"message": "Ticket canceled successfully"}), 200

@app.route('/api/v1/tickets/booked', methods=['GET'])
def get_booked_tickets():
    booked_tickets = Ticket.query.filter(or_(Ticket.status == 'confirmed', Ticket.status == 'RAC')).all()
    result = []
    for ticket in booked_tickets:
        passengers_data = [
            {"name": passenger.name, "age": passenger.age, "gender": passenger.gender}
            for passenger in ticket.passengers
        ]
        result.append({
            "ticket_id": ticket.id,
            "status": ticket.status,
            "berth_number": ticket.berth_number,
            "passengers": passengers_data
        })
    return jsonify(result), 200

@app.route('/api/v1/tickets/available', methods=['GET'])
def get_available_tickets():
    available_berths = Berth.query.filter_by(is_occupied=False).all()
    result = [{"berth_number": berth.berth_number, "type": berth.type} for berth in available_berths]
    return jsonify({"available_berths": result}), 200

# Run the application
if __name__ == '__main__':
    app.run(debug=True)