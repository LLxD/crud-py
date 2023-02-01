from flask import Flask
from sqlalchemy.orm import sessionmaker
from models import User, Airport, Flight, Booking, engine
from utils import generate_token, send_to_rabbit_mq, seed_database
import json

app = Flask(__name__)

# Create a new session
Session = sessionmaker(bind=engine)
# session = Session()

# User handlers

@app.route('/view_users', methods=['GET'])
def view_users():
    session = Session()
    users = session.query(User).all()
    return str(users)


@app.route('/login/<email>/<password>', methods=['POST'])
def login(email, password):
    session = Session()
    user = session.query(User).filter_by(
        email=email, password=password).first()
    if user:
        token = generate_token(email, password)
        user.token = token
        session.commit()
        return json.dumps({"token": token})
    else:
        return json.dumps({"error": "User not found"})


@app.route('/logout/<token>', methods=['GET'])
def logout(token):
    session = Session()
    user = session.query(User).filter_by(token=token).first()
    if user:
        user.token = ""
        session.commit()
        return json.dumps({"success": "User logged out"})
    else:
        return json.dumps({"error": "User not found"})


@app.route('/validate_account/<token>', methods=['POST'])
def validate_account(token):
    session = Session()
    user = session.query(User).filter_by(token=token).first()
    if user:
        return json.dumps({"success": "User validated"})
    else:
        return json.dumps({"error": "User not found"})


@app.route('/create_account/<email>/<password>', methods=['POST'])
def create_account(email, password):
    session = Session()
    # check if the user already exists
    user = session.query(User).filter_by(email=email).first()
    if user:
        return "User already exists"
    else:
        token = generate_token(email, password)
        user = User(email=email, password=password, token=token)
        session.add(user)
        session.commit()
        return token

# Airports and flights handlers


@app.route('/view_airports', methods=['GET'])
def view_airports():
    session = Session()
    airports = session.query(Airport).all()
    return str(airports)


@app.route('/view_airports/<origin>', methods=['GET'])
def view_airports_by_origin(origin):
    session = Session()
    airports = session.query(Airport).filter_by(origin=origin).all()
    return str(airports)


@app.route('/view_flights', methods=['GET'])
def view_flights():
    session = Session()
    flights = session.query(Flight).all()
    session.close()
    return str(flights)


@app.route('/view_flights/<origin>/<destination>/<desired_capacity>', methods=['GET'])
def view_flights_by_origin_destination_lower_price_min_capacity(origin, destination, desired_capacity):
    session = Session()
    flights = session.query(Flight).filter_by(
        origin=origin, destination=destination).all()
    flights = [flight for flight in flights if flight.max_capacity >=
               int(desired_capacity)]
    return str(flights)


@app.route('/flight_capacity/<flight_id>/<desired_capacity>', methods=['PUT'])
def update_flight_capactity(flight_id, desired_capacity):
    session = Session()
    # decrease the capacity of the flight by the number of people
    flight = session.query(Flight).filter_by(id=flight_id).first()
    flight.max_capacity = int(desired_capacity)
    session.commit()
    return json.dumps({"success": "Flight capacity updated"})



# Booking handlers


@app.route('/book_flight/<user_id>/<flight_id>/<date>/<tickets_wanted>', methods=['POST'])
def book_flight(user_id, flight_id, date, tickets_wanted):
    session = Session()
    user_id = int(user_id)
    flight_id = int(flight_id)
    tickets_wanted = int(tickets_wanted)

    booking = Booking(user_id=user_id, flight_id=flight_id, date=date)
    session.add(booking)
    session.commit()
    flight = session.query(Flight).filter_by(id=flight_id).first()
    flight.max_capacity -= int(tickets_wanted)
    session.commit()
    send_to_rabbit_mq(str(booking))
    return json.dumps({"success": "Flight booked", "booking": str(booking)})





if __name__ == '__main__':
    session = Session()
    if not session.query(Airport).all():
        print("Seeding the database")
        seed_database(session)

    app.run(host="0.0.0.0", port=5000)
