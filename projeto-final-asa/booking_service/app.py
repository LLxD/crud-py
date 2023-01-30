from flask import Flask
from sqlalchemy.orm import sessionmaker
from models import Booking, engine
import pika
import requests

app = Flask(__name__)

# Create a new session
Session = sessionmaker(bind=engine)
# session = Session()


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
    # so there is an internal call to airport service
    requests.put(
        f'http://localhost:4000/flight_capacity/{flight_id}/{tickets_wanted}')
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
    app.run(host="0.0.0.0", port=5000)
