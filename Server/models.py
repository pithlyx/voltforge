
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
from services import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    api_key = db.Column(UUID(as_uuid=True), unique=True,
                        nullable=False, default=uuid.uuid4)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    chunk = db.Column(db.Tuple)
    relative_pos = db.Column(db.Tuple)
    upgraded_at = db.Column(db.DateTime)
    level = db.Column(db.Integer)
    resources = db.Column(JSON)
    online = db.Column(db.Boolean)
    updated = db.Column(db.DateTime)
    users = db.relationship('User', backref='city', lazy=True)
    outposts = db.relationship('Outpost', backref='city', lazy=True)


class Outpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    chunk = db.Column(db.Tuple)
    relative_pos = db.Column(db.Tuple)
    level = db.Column(db.Integer)
    resources = db.Column(JSON)
    buildings = db.relationship('Buildings', backref='outpost', lazy=True)


class Buildings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer)
    level = db.Column(db.Integer)
    outpost_id = db.Column(db.Integer, db.ForeignKey('outpost.id'))
    relative_pos = db.Column(db.Tuple)
    resource = db.Column(db.String(120))
    rate = db.Column(db.Integer)
