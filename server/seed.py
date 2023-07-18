from services import app
from models import db

with app.app_context():
    db.drop_all()
    db.create_all()
