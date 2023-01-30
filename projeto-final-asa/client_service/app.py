from flask import Flask
from sqlalchemy.orm import sessionmaker
from models import User, engine
import hashlib

app = Flask(__name__)

# Create a new session
Session = sessionmaker(bind=engine)
# session = Session()


def generate_token(email, password):
    m = hashlib.sha256()
    m.update(email.encode('utf-8'))
    m.update(password.encode('utf-8'))
    return m.hexdigest()


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


if __name__ == '__main__':
    app.run(port=3000)
