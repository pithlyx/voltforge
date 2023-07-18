from services import db, app, api, bcrypt, cipher_suite
from models import User
import dotenv
import uuid
import os
from flask import Flask, request, make_response, jsonify, session
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm.exc import NoResultFound

dotenv.load_dotenv()

server_port = os.getenv('SRV_PORT')


def encode_key(key):
    return cipher_suite.encrypt(key.encode()).decode()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    try:
        if api_key := request.headers.get('Authorization'):
            encoded_key = encode_key(api_key)
            user = User.query.filter_by(api_key=encoded_key).one()
            login_user(user)
        else:
            # authenticate using username and password
            user = User.query.filter_by(username=username).one()
            if not user.auth(password=password):
                return make_response(jsonify({'message': 'Invalid credentials!'}), 400)
            login_user(user)
            user.api_key = user.get_key()
        return make_response(jsonify({'message': 'Login successful!', 'user': user.to_dict()}), 200)
    except NoResultFound:
        return make_response(jsonify({'message': 'Invalid credentials!'}), 400)


@app.route('/logout', methods=['POST'])
def logout():
    if auth_header := request.headers.get('Authorization'):
        api_key = auth_header.split(" ")[1]
        # encrypt the provided API key
        encrypted_api_key = cipher_suite.encrypt(api_key.encode()).decode()
        print(encrypted_api_key)
        if user := User.query.filter_by(api_key=encrypted_api_key).first():
            logout_user()
            return make_response(jsonify({'message': 'Logout successful!'}), 200)
    return make_response(jsonify({'message': 'Invalid credentials!'}), 400)


@app.route('/users', methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET':
        users = User.query.all()
        return make_response(jsonify({'users': [user.to_dict() for user in users]}), 200)

    elif request.method == 'POST':
        try:
            data = request.get_json()
            username = data['username']
            password = data['password']
            email = data['email']
            if User.query.filter_by(username=username).first():
                return make_response(jsonify({'message': 'User already exists!'}), 400)
            else:
                user = User(username=username, password=password, email=email)
                db.session.add(user)
                db.session.commit()
                user.api_key = user.get_key()
                return make_response(jsonify({'message': 'User created successfully!',
                                              'user': user.to_dict()}), 201)
        except KeyError:
            return make_response(jsonify({'message': 'Invalid request!'}), 400)


@app.route('/', methods=['GET'])
def index():
    return make_response(jsonify({'message': 'Hello world!'}), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=server_port)
