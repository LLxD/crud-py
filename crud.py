from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import pika
import hashlib
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crud.db'
db = SQLAlchemy(app)
con = sqlite3.connect("./instance/crud.db")  
print("Database opened successfully")
con.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT, token TEXT)")
con.execute("CREATE TABLE IF NOT EXISTS airports (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, origin TEXT)")
con.execute("CREATE TABLE IF NOT EXISTS flights (id INTEGER PRIMARY KEY AUTOINCREMENT, origin TEXT, destination TEXT, price TEXT, max_capacity NUMERIC)")
con.execute("CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, flight_id TEXT, date TEXT)")
print("Tables created successfully")  
con.close()


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

class Airport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    origin = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return json.dumps(to_dict(self))
        
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    price = db.Column(db.String(120), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return json.dumps(to_dict(self))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    flight_id = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return json.dumps(to_dict(self))

def generate_token(email, password):
    m = hashlib.sha256()
    m.update(email.encode('utf-8'))
    m.update(password.encode('utf-8'))
    return m.hexdigest()



@app.route('/login/<email>/<password>', methods=['GET'])
def login(email, password):
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        token = generate_token(email, password)
        user.token = token
        db.session.commit()
        return token
    else:
        return "User not found"

@app.route('/logout/<token>', methods=['GET'])
def logout(token):
    user = User.query.filter_by(token=token).first()
    if user:
        user.token = ""
        db.session.commit()
        return "Logged out"
    else:
        return "User not found"

@app.route('/create_account/<email>/<password>', methods=['POST'])
def create_account(email, password):
    # check if the user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        return "User already exists"
    else:
        token = generate_token(email, password)
        user = User(email=email, password=password, token=token)
        db.session.add(user)
        db.session.commit()
        return token
        

@app.route('/view_airports', methods=['GET'])
def view_airports():
    airports = Airport.query.all()
    return str(airports)

@app.route('/view_airports/<origin>', methods=['GET'])
def view_airports_by_origin(origin):
    airports = Airport.query.filter_by(origin=origin).all()
    return str(airports)

@app.route('/view_flights', methods=['GET'])
def view_flights():
    flights = Flight.query.all()
    return str(flights)

@app.route('/view_flights/<origin>/<destination>/<desired_capacity>', methods=['GET'])
def view_flights_by_origin_destination_lower_price_min_capacity(origin, destination, desired_capacity):
    flights = Flight.query.filter_by(origin=origin, destination=destination).all()
    flights = [flight for flight in flights if flight.max_capacity >= int(desired_capacity) ]
    return str(flights)

@app.route('/book_flight/<user_id>/<flight_id>/<date>/<tickets_wanted>', methods=['POST'])
def book_flight(user_id, flight_id, date, tickets_wanted):
    user_id = int(user_id)
    flight_id = int(flight_id)
    tickets_wanted = int(tickets_wanted)
    
    booking = Booking(user_id=user_id, flight_id=flight_id, date=date)
    db.session.add(booking)
    db.session.commit()
    # it also should decrease the capacity of the flight by the number of people
    flight = Flight.query.filter_by(id=flight_id).first()
    flight.max_capacity -= int(tickets_wanted)
    db.session.commit()
    # send the booking to the rabbitmq server
    send_to_rabbit_mq(str(booking))
    return "Flight booked"


def send_to_rabbit_mq(flight_data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='broker'))
    channel = connection.channel()
    channel.queue_declare(queue='flights')
    channel.basic_publish(exchange='', routing_key='flights', body=flight_data)
    connection.close()

def seed_database():
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

    db.session.add_all(airports)
    db.session.add_all(flights)
    db.session.commit()


if __name__ == '__main__':
    # erase the database and create a new one
    app.app_context().push()
    db.drop_all()
    db.create_all()
    seed_database()
    app.run(host="0.0.0.0",debug=True)

