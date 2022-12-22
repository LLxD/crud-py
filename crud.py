# using the flask framework and the sqlalchemy ORM
# this file contains the CRUD operations for the database
# its going to store the data in a sqlite database
# the database is going to be called crud.db
# the database is going to have 1 table called students

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import pika


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crud.db'
db = SQLAlchemy(app)
con = sqlite3.connect("./instance/crud.db")  
print("Database opened successfully")  
con.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, grade INTEGER NOT NULL)")
print("Table created successfully")  
con.close()  

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    grade = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Students %r>' % self.name

## create an api endpoint to every operation from CRUD

# create
## every time we create a new student we are going to send a message to the queue
## the message is going to be the name of the student and the grade
## the queue is going to be called students
## the message is going to be sent to the exchange called students
## the rabbit mq server is going to be running on the localhost, port 5672
@app.route('/create/<name>/<grade>')
def create(name, grade):
    student = Students(name=name, grade=grade)
    db.session.add(student)
    db.session.commit()
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='broker'))
    channel = connection.channel()
    channel.exchange_declare(exchange='students', exchange_type='fanout')
    channel.basic_publish(exchange='students', routing_key='', body=name + " " + grade)
    connection.close()
    return 'Student created!'

# read
@app.route('/')
def read():
    students = Students.query.all()
    output = []
    for student in students:
        student_data = {'name': student.name, 'grade': student.grade}
        output.append(student_data)
    return {'students': output}

# update
@app.route('/update/<name>/<grade>')
def update(name, grade):
    student = Students.query.filter_by(name=name).first()
    student.grade = grade
    db.session.commit()
    return 'Student updated!'

# delete
@app.route('/delete/<name>')
def delete(name):
    student = Students.query.filter_by(name=name).first()
    db.session.delete(student)
    db.session.commit()
    return 'Student deleted!'

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)

