from services import db, app, cipher_suite
from models import User, City, Building, Outpost
import dotenv
import os
from flask import request, make_response, jsonify
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import text
import numpy as np
from proc_map import Map

m = Map()

dotenv.load_dotenv()

server_port = os.getenv('SRV_PORT')


def encode_key(key):
    return cipher_suite.encrypt(key.encode()).decode()


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
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
            return make_response(jsonify({'message': 'Login successful!'}), 200)
        except NoResultFound:
            return make_response(jsonify({'message': 'Invalid credentials!'}), 400)
    elif request.method == 'GET':
        if current_user.is_authenticated:
            return make_response(jsonify({'message': 'Already logged in!'}), 200)
        return make_response(jsonify({'message': 'Not logged in!'}), 400)


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return make_response(jsonify({'message': 'Logout successful!'}), 200)


@app.route('/users', methods=['GET', 'POST', "PATCH"])
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
            if User.query.filter_by(email=email).first():
                return make_response(jsonify({'message': 'Email already exists!'}), 400)
            user = User(username=username, password=password,
                        email=email, position=rand_pos)
            print(user.position)
            db.session.add(user)
            db.session.commit()
            user.api_key = user.get_key()
            return make_response(jsonify({'message': 'User created successfully!'}), 201)
        except KeyError:
            return make_response(jsonify({'message': 'Invalid request!'}), 400)
        except Exception as e:
            return make_response(jsonify({'message': f'Error: {e}'}), 400)
    elif request.method == 'PATCH':
        if current_user.is_authenticated:
            data = request.get_json()
            if data.get('username'):
                current_user.username = data.get('username')
            if data.get('password'):
                current_user.password = data.get('password')
            if data.get('email'):
                current_user.email = data.get('email')
            if data.get('position'):
                current_user.position = data.get('position')
            db.session.commit()
            return make_response(jsonify({'message': 'User updated successfully!'}), 200)

@app.route('/map', methods=['GET', 'POST'])
@login_required
def handle_map():
    if request.method == 'GET':
        x = int(request.args.get('x') or current_user.position[0])
        y = int(request.args.get('y') or current_user.position[1])
        r = int(request.args.get('r') or "100")
        region = m.get_region(x, y, r)

        # Query for buildings and outposts within the specified range
        buildings = Building.query.filter(text(
            "(coord->>0)::int between :xmin and :xmax and (coord->>1)::int between :ymin and :ymax")).params(xmin=x-r, xmax=x+r, ymin=y-r, ymax=y+r).all()
        outposts = Outpost.query.filter(text(
            "(coord->>0)::int between :xmin and :xmax and (coord->>1)::int between :ymin and :ymax")).params(xmin=x-r, xmax=x+r, ymin=y-r, ymax=y+r).all()

        return make_response(jsonify({'center': [x, y],
                                      "map_data": region,
                                      "buildings": [building.to_dict() for building in buildings],
                                      "outposts": [outpost.to_dict() for outpost in outposts]}), 200)
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        pos = data.get('closestTile')
        current_user.position = pos
        db.session.commit()
        return make_response(jsonify({'message': 'Position updated successfully!',
                                      'position': current_user.position}), 200)


@app.route('/city', methods=['GET', 'POST'])
@login_required
def handle_cities():
    if request.method == 'GET':
        if cities := City.query.filter_by(id=current_user.city_id).all():
            return make_response(jsonify({'cities': [city.to_dict() for city in cities]}), 200)
        else:
            return make_response(jsonify({'message': 'No cities found for current user!'}), 400)
    elif request.method == 'POST':
        try:
            if current_user.city_id:
                return make_response(jsonify({'message': 'City already exists!'}), 400)
            data = request.get_json()
            city_name = data.get('city_name')
            city = City(name=city_name, level=1)
            current_user.city = city
            db.session.add_all([city, current_user])
            db.session.commit()
            return make_response(jsonify({'message': 'City created successfully!',
                                          'city': city.to_dict()}), 200)
        except Exception as e:
            return make_response(jsonify({'message': f'Error: {e}'}), 400)


@app.route('/outpost', methods=['GET', 'POST', 'DELETE'])
@login_required
def handle_outpost():
    if request.method == 'GET':
        outposts = City.query.filter_by(id=current_user.city_id).one().outposts
        for outpost in outposts:
            outpost.serialize_rules = ('-city',)
            # outpost.to_dict()  # serialize
        return make_response(jsonify({'outposts': [outpost.to_dict() for outpost in outposts]}), 200)

    elif request.method == 'POST':
        if len(current_user.city.outposts) > 2*current_user.city.level:
            return make_response(jsonify({'message': 'You cannot place any more outposts!'}), 400)
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        if Outpost.query.filter(text("(coord->>0)::int = :x and (coord->>1)::int = :y")).params(x=x, y=y).first() or Building.query.filter(text("(coord->>0)::int = :x and (coord->>1)::int = :y")).params(x=x, y=y).first():
            return make_response(jsonify({'message': 'There is already a building here!'}), 400)
        outpost = Outpost(city_id=current_user.city_id, coord=[x, y], level=1, resources={
                          "wood": 0, "stone": 0, "iron": 0, "coal": 0})
        db.session.add(outpost)
        db.session.commit()
        outpost.serialize_rules = ('-city',)
        return make_response(jsonify({'message': 'Outpost created successfully!',
                                      "outpost": outpost.to_dict()}), 201)

    elif request.method == 'DELETE':
        data = request.get_json()
        x = data.get('x')
        y = data.get('y')
        outpost = Outpost.query.filter(
            text("(coord->>0)::int = :x and (coord->>1)::int = :y")).params(x=x, y=y).first()
        if y and x and outpost and outpost.city_id == current_user.city_id:
            db.session.delete(outpost)
            db.session.commit()
            return make_response(jsonify({'message': 'Outpost deleted successfully!'}), 200)
        return make_response(jsonify({'message': 'Target outpost does not exist'}), 400)


@app.route('/', methods=['GET'])
def index():
    return make_response(jsonify({'message': 'Hello world!'}), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=server_port)
