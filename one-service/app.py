from flask import Flask
from sqlalchemy.orm import sessionmaker
from models import User, Airport, Flight, Booking, engine
import hashlib
# import pika

app = Flask(__name__)

# Create a new session
Session = sessionmaker(bind=engine)
# session = Session()

# User handlers


def generate_token(email, password):
    m = hashlib.sha256()
    m.update(email.encode('utf-8'))
    m.update(password.encode('utf-8'))
    return m.hexdigest()


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
        return token
    else:
        return "User not found"


@app.route('/logout/<token>', methods=['GET'])
def logout(token):
    session = Session()
    user = session.query(User).filter_by(token=token).first()
    if user:
        user.token = ""
        session.commit()
        return "Logged out"
    else:
        return "User not found"


@app.route('/validate_account/<token>', methods=['POST'])
def validate_account(token):
    session = Session()
    user = session.query(User).filter_by(token=token).first()
    if user:
        return 'valid user'
    else:
        return 'invalid user'


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
    # airports = Airport.query.filter_by(origin=origin).all()
    airports = session.query(Airport).filter_by(origin=origin).all()
    return str(airports)


@app.route('/view_flights', methods=['GET'])
def view_flights():
    session = Session()
    # flights = Flight.query.all()
    flights = session.query(Flight).all()
    session.close()
    return str(flights)


@app.route('/view_flights/<origin>/<destination>/<desired_capacity>', methods=['GET'])
def view_flights_by_origin_destination_lower_price_min_capacity(origin, destination, desired_capacity):
    # flights = Flight.query.filter_by(origin=origin, destination=destination).all()
    session = Session()
    flights = session.query(Flight).filter_by(
        origin=origin, destination=destination).all()
    flights = [flight for flight in flights if flight.max_capacity >=
               int(desired_capacity)]
    return str(flights)


@app.route('/flight_capacity/<flight_id>/<tickets_wanted>', methods=['POST'])
def update_flight_capactity(flight_id, tickets_wanted):
    session = Session()
    # decrease the capacity of the flight by the number of people
    flight = session.query(Flight).filter_by(id=flight_id).first()
    flight.max_capacity -= int(tickets_wanted)
    session.commit()
    return {"status": flight.max_capacity}


def seed_database():
    session = Session()
    # seed the database
    airports = [
        Airport(name="ORD", origin="Chicago"),
        Airport(name="ATL", origin="Atlanta"),
        Airport(name="DFW", origin="Dallas"),
        Airport(name="DEN", origin="Denver"),
        Airport(name="LAX", origin="Los Angeles"),
    ]

    flights = [
        Flight(origin="ORD", destination="ATL", price="100", max_capacity=10),
        Flight(origin="ORD", destination="DFW", price="200", max_capacity=20),
        Flight(origin="ORD", destination="DEN", price="300", max_capacity=30),
        Flight(origin="ORD", destination="ATL", price="400", max_capacity=40),
        Flight(origin="ATL", destination="ORD", price="100", max_capacity=10),
        Flight(origin="ATL", destination="DFW", price="200", max_capacity=20),
        Flight(origin="ATL", destination="DEN", price="300", max_capacity=30),
        Flight(origin="ATL", destination="ATL", price="400", max_capacity=40),
        Flight(origin="DFW", destination="ORD", price="100", max_capacity=10),
        Flight(origin="DFW", destination="ATL", price="200", max_capacity=20),
        Flight(origin="DFW", destination="DEN", price="300", max_capacity=30),
        Flight(origin="DFW", destination="ATL", price="400", max_capacity=40),
        Flight(origin="DEN", destination="ORD", price="100", max_capacity=10),
        Flight(origin="DEN", destination="ATL", price="200", max_capacity=20),
        Flight(origin="DEN", destination="DFW", price="300", max_capacity=30),
        Flight(origin="DEN", destination="ATL", price="400", max_capacity=40),
    ]

    session.add_all(airports)
    session.add_all(flights)
    session.commit()
    session.close()

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
    # it also should decrease the capacity of the flight by the number of people
    flight = session.query(Flight).filter_by(id=flight_id).first()
    flight.max_capacity -= int(tickets_wanted)
    session.commit()
    # send the booking to the rabbitmq server
    # send_to_rabbit_mq(str(booking))
    return "Flight booked"


def send_to_rabbit_mq(flight_data):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='broker'))
    channel = connection.channel()
    channel.queue_declare(queue='flights')
    channel.basic_publish(exchange='', routing_key='flights', body=flight_data)
    connection.close()


if __name__ == '__main__':
    session = Session()
    if not session.query(Airport).all():
        print("Seeding the database")
        seed_database()

    app.run(host="0.0.0.0", port=5000)
