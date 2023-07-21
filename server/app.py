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


def get_request_data():
    return request.get_json()


def handle_response(message, status):
    return make_response(jsonify({'message': message}), status)


def authenticate_user(username, password):
    try:
        # authenticate using username and password
        user = User.query.filter_by(username=username).one()
        if not user.auth(password=password):
            return False
        login_user(user, remember=True)
        user.api_key = user.get_key()
        return True
    except NoResultFound:
        return False


def is_user_authenticated():
    return bool(current_user.is_authenticated)


def check_existing_user(username, email):
    return bool(
        User.query.filter_by(username=username).first()
        or User.query.filter_by(email=email).first()
    )


def delete_city_and_related(city, user):
    # Delete all outposts and associated buildings of the city
    for outpost in city.outposts:
        Building.query.filter_by(outpost_id=outpost.id).delete()
        db.session.delete(outpost)

    # Delete the city
    db.session.delete(city)

    # Delete the user
    db.session.delete(user)

    db.session.commit()


def get_coordinates():
    x = int(request.args.get('x') or current_user.position[0])
    y = int(request.args.get('y') or current_user.position[1])
    r = int(request.args.get('r') or "50")
    return x, y, r


def check_if_building_exists(x, y):
    return bool(
        Outpost.query.filter(
            text("(coord->>0)::int = :x and (coord->>1)::int = :y")
        )
        .params(x=x, y=y)
        .first()
        or Building.query.filter(
            text("(coord->>0)::int = :x and (coord->>1)::int = :y")
        )
        .params(x=x, y=y)
        .first()
    )


def create_building(x, y, id, current_user):
    print()
    print()
    print(f"Creating building at ({x}, {y}) with id {id}")
    print()
    print()
    if id == 0:
        # This is an outpost
        if len(current_user.city.outposts) > 2*current_user.city.level:
            return handle_response('You cannot place any more outposts!', 400)

        outpost = Outpost(city_id=current_user.city_id, coord=[x, y], level=1, resources={
            "wood": 0, "stone": 0, "iron": 0, "coal": 0})
        db.session.add(outpost)
    else:
        # This is a building
        # First, check if the building is within 20 units of an outpost
        outpost = Outpost.query.filter(text(
            "abs((coord->>0)::int - :x) <= 20 and abs((coord->>1)::int - :y) <= 10 and city_id = :city_id")).params(x=x, y=y, city_id=current_user.city_id).order_by(text("abs((coord->>0)::int - :x) + abs((coord->>1)::int - :y)")).first()

        if not outpost:
            return handle_response('No outpost found within 10 units of this location!', 400)

        building = Building(building_id=id, level=1, outpost_id=outpost.id, coord=[
            x, y], resource=None, rate=None)
        db.session.add(building)

    db.session.commit()
    return handle_response('Building placed successfully!', 200)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return (
            handle_response('Already logged in!', 200)
            if is_user_authenticated()
            else handle_response('Not logged in!', 400)
        )
    elif request.method == 'POST':
        data = get_request_data()
        username = data.get('username')
        password = data.get('password')
        if is_user_authenticated():
            return handle_response('Already logged in!', 400)
        return (
            handle_response('Login successful!', 200) if authenticate_user(
                username, password) else handle_response('Invalid credentials!', 400)
        )


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return handle_response('Logout successful!', 200)


@app.route('/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def create_user():
    if request.method == 'GET':
        print("getting users")
        users = User.query.all()
        return make_response(jsonify({'users': [user.to_dict() for user in users]}), 200)

    elif request.method == 'POST':
        try:
            data = get_request_data()
            username = data['username']
            password = data['password']
            email = data['email']
            city_name = data['city_name']
            rand_pos = [np.random.randint(5000), np.random.randint(5000)]

            # Check if a user with the provided username or email already exists
            if check_existing_user(username, email):
                return handle_response('User or email already exists!', 400)

            # Check if a city with the provided city_name already exists
            city = City.query.filter_by(name=city_name).first()
            if city is None:
                # Create a new city if it doesn't exist
                city = City(name=city_name, level=1)
                db.session.add(city)
                db.session.commit()

            user = User(username=username, password=password,
                        email=email, position=rand_pos, city_id=city.id)

            print(user.position)
            db.session.add(user)
            db.session.commit()
            user.api_key = user.get_key()
            return handle_response('User created successfully!', 201)
        except KeyError:
            return handle_response('Invalid request!', 400)
        except Exception as e:
            return handle_response(f'Error: {e}', 400)

    elif request.method == 'DELETE':
        if not is_user_authenticated():
            return handle_response('Not logged in!', 400)
        try:
            # Check if there are any other users associated with the user's city
            other_users = User.query.filter_by(
                city_id=current_user.city_id).all()
            if len(other_users) > 1:
                return handle_response('There are other users in this city, can\'t delete city!', 400)

            # Get the city
            city = City.query.filter_by(id=current_user.city_id).first()

            delete_city_and_related(city, current_user)

            return handle_response('User, city, outposts and buildings deleted successfully!', 200)

        except Exception as e:
            return handle_response(f'Error: {e}', 400)


@app.route('/map', methods=['GET', 'POST'])
@login_required
def handle_map():
    if request.method == 'GET':
        x, y, r = get_coordinates()
        region = m.get_region(x, y, r)

        # Query for buildings and outposts within the specified range
        buildings = Building.query.filter(text(
            "(coord->>0)::int between :xmin and :xmax and (coord->>1)::int between :ymin and :ymax")).params(xmin=x-r, xmax=x+r, ymin=y-r, ymax=y+r).all()
        outposts = Outpost.query.filter(text(
            "(coord->>0)::int between :xmin and :xmax and (coord->>1)::int between :ymin and :ymax")).params(xmin=x-r, xmax=x+r, ymin=y-r, ymax=y+r).all()
        for outpost in outposts:
            outpost.serialize_rules = ('-buildings', '-city',)
        return make_response(jsonify({"center": [x, y],
                                      "map_data": region,
                                      "buildings": [building.to_dict() for building in buildings],
                                      "outposts": [outpost.to_dict() for outpost in outposts]}), 200)
    if request.method == 'POST':
        data = get_request_data()
        print(data)
        pos = data.get('position')
        current_user.position = pos
        db.session.commit()
        return handle_response('Position updated successfully!', 200)


@app.route('/city', methods=['GET', 'POST'])
@login_required
def handle_cities():
    if request.method == 'GET':
        if cities := City.query.filter_by(id=current_user.city_id).all():
            return make_response(jsonify({'cities': [city.to_dict() for city in cities]}), 200)
        else:
            return handle_response('No cities found for current user!', 400)
    elif request.method == 'POST':
        try:
            if current_user.city_id:
                return handle_response('City already exists!', 400)
            data = get_request_data()
            city_name = data.get('city_name')
            city = City(name=city_name, level=1)
            current_user.city = city
            db.session.add_all([city, current_user])
            db.session.commit()
            return handle_response('City created successfully!', 200)
        except Exception as e:
            return handle_response(f'Error: {e}', 400)


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
        data = get_request_data()
        x = data.get('x')
        y = data.get('y')

        if check_if_building_exists(x, y):
            return handle_response('There is already a building here!', 400)

        return create_building(x, y, 1, current_user)

    elif request.method == 'DELETE':
        data = get_request_data()
        x = data.get('x')
        y = data.get('y')
        outpost = Outpost.query.filter(
            text("(coord->>0)::int = :x and (coord->>1)::int = :y")).params(x=x, y=y).first()
        if y and x and outpost and outpost.city_id == current_user.city_id:
            db.session.delete(outpost)
            db.session.commit()
            return handle_response('Outpost deleted successfully!', 200)
        return handle_response('Target outpost does not exist', 400)


@app.route('/buildings', methods=['POST', 'DELETE'])
@login_required
def handle_buildings():
    if request.method == 'POST':
        data = get_request_data()
        x = data.get('x')
        y = data.get('y')
        id = data.get('id')

        if check_if_building_exists(x, y):
            return handle_response('There is already a building here!', 400)

        return create_building(x, y, id, current_user)

    elif request.method == "DELETE":
        data = get_request_data()
        x = data.get('x')
        y = data.get('y')
        building = Building.query.filter(
            text("(coord->>0)::int = :x and (coord->>1)::int = :y")).params(x=x, y=y).first()
        if y and x and building and building.outpost.city_id == current_user.city_id:
            db.session.delete(building)
            db.session.commit()
            return handle_response('Building deleted successfully!', 200)
        return handle_response('Target building does not exist', 400)


@app.route('/', methods=['GET'])
def index():
    return handle_response('Hello world!', 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=server_port)
