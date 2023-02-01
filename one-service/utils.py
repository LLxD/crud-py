import hashlib
import pika
from models import User, Airport, Flight, Booking, engine

def generate_token(email, password):
    m = hashlib.sha256()
    m.update(email.encode('utf-8'))
    m.update(password.encode('utf-8'))
    return m.hexdigest()

def send_to_rabbit_mq(flight_data):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='broker'))
    channel = connection.channel()
    channel.queue_declare(queue='flights')
    channel.basic_publish(exchange='', routing_key='flights', body=flight_data)
    connection.close()


def seed_database(session):
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