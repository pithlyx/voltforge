import secrets
import uuid

from sqlalchemy import event
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
from services import db, bcrypt, cipher_suite
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin


class User(UserMixin, db.Model, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ('-password', '-city_id')
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    api_key = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))

    def auth(self, password=None, api_key=None):
        if password:
            return bcrypt.check_password_hash(self.password, password)
        elif api_key:
            return self.api_key == api_key

    def get_key(self):
        return cipher_suite.decrypt(self.api_key.encode()).decode()


@event.listens_for(User, 'before_insert')
def handle_security(mapper, connection, target):
    # Hash the password using Flask-Bcrypt
    target.password = bcrypt.generate_password_hash(
        target.password).decode('utf-8')
    # Encrypt the API key using Fernet
    api_key = secrets.token_hex(16).encode()
    encrypted_key = cipher_suite.encrypt(api_key)
    target.api_key = encrypted_key.decode()


class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    chunk = db.Column(ARRAY(db.Integer))
    relative_pos = db.Column(ARRAY(db.Integer))
    upgraded_at = db.Column(db.DateTime)
    level = db.Column(db.Integer)
    resources = db.Column(JSON)
    online = db.Column(db.Boolean)
    updated = db.Column(db.DateTime)
    users = db.relationship('User', backref='cities', lazy=True)
    outposts = db.relationship('Outpost', backref='cities', lazy=True)


class Outpost(db.Model):
    __tablename__ = 'outposts'

    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    chunk = db.Column(ARRAY(db.Integer))
    relative_pos = db.Column(ARRAY(db.Integer))
    level = db.Column(db.Integer)
    resources = db.Column(JSON)
    # Update relationship name
    buildings = db.relationship('Building', backref='outpost', lazy=True)


class Building(db.Model):
    __tablename__ = 'buildings'
    serialize_only = ('id', 'building_id', 'level',
                      'outpost_id', 'relative_pos', 'resource', 'rate')

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer)
    level = db.Column(db.Integer)
    outpost_id = db.Column(db.Integer, db.ForeignKey('outposts.id'))
    relative_pos = db.Column(ARRAY(db.Integer))
    resource = db.Column(db.String(120))
    rate = db.Column(db.Integer)
