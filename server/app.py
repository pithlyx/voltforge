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
from datetime import datetime, timedelta, timezone
import numpy as np
dotenv.load_dotenv()

server_port = os.getenv('SRV_PORT')


def encode_key(key):
    return cipher_suite.encrypt(key.encode()).decode()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if current_user.is_authenticated:
        return make_response(jsonify({'message': 'Already logged in!'}), 400)
    try:
        # authenticate using username and password
        user = User.query.filter_by(username=username).one()
        if not user.auth(password=password):
            return make_response(jsonify({'message': 'Invalid credentials!'}), 400)
        login_user(user, remember=True)
        user.api_key = user.get_key()
        return make_response(jsonify({'message': 'Login successful!', 'user': user.to_dict()}), 200)
    except NoResultFound:
        return make_response(jsonify({'message': 'Invalid credentials!'}), 400)


@app.route('/logout', methods=['POST'])
def logout():
    if not current_user.is_authenticated:
        return make_response(jsonify({'message': 'Not logged in!'}), 400)
    logout_user()
    return make_response(jsonify({'message': 'Logout successful!'}), 200)


@app.route('/users', methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET':
        print("getting users")
        users = User.query.all()
        return make_response(jsonify({'users': [user.to_dict() for user in users]}), 200)

    elif request.method == 'POST':
        try:
            data = request.get_json()
            username = data['username']
            password = data['password']
            email = data['email']
            rand_pos = [np.random.randint(5000), np.random.randint(5000)]
            if User.query.filter_by(username=username).first():
                return make_response(jsonify({'message': 'User already exists!'}), 400)
            else:
                user = User(username=username, password=password,
                            email=email, position=rand_pos)
                print(user.position)
                db.session.add(user)
                db.session.commit()
                user.api_key = user.get_key()
                return make_response(jsonify({'message': 'User created successfully!',
                                              'user': user.to_dict()}), 201)
        except KeyError:
            return make_response(jsonify({'message': 'Invalid request!'}), 400)
        except Exception as e:
            return make_response(jsonify({'message': f'Error: {e}'}), 400)


@app.route('/map', methods=['GET', 'POST'])
@login_required
def handle_map():
    if request.method == 'GET':
        from proc_map import Map
        m = Map()
        x = int(request.args.get('x') or current_user.position[0])
        y = int(request.args.get('y') or current_user.position[1])
        r = int(request.args.get('r') or "50")
        region = m.get_region(x, y, r)
        return make_response(jsonify({"x": x,
                                      "y": y,
                                      "map": region}), 200)
    if request.method == 'POST':
        from proc_map import Map
        m = Map()
        region = m.get_region(int(x), int(y), 20)
        return make_response(jsonify({"x": x,
                                      "y": y,
                                      "r": r,
                                      "map": region}), 200)


@app.route('/init ')
@app.route('/', methods=['GET'])
def index():
    return make_response(jsonify({'message': 'Hello world!'}), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=server_port)
