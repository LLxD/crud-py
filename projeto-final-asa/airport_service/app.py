from flask import Flask
from sqlalchemy.orm import sessionmaker
from models import Airport, Flight, engine
import json


app = Flask(__name__)

# Create a new session
Session = sessionmaker(bind=engine)
# session = Session()


@app.route('/view_airports', methods=['GET'])
def view_airports():
    session = Session()
    # airports = Airport.query.all()
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
    session.close()
    return str(flights)


@app.route('/flight_capacity/<flight_id>/<tickets_wanted>', methods=['PUT'])
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


if __name__ == '__main__':
    session = Session()
    if not session.query(Airport).all():
        print("Seeding the database")
        seed_database()

    app.run(host="0.0.0.0", port=4000)
