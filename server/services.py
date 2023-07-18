from dotenv import load_dotenv
import os
from sqlalchemy import MetaData
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
from flask_login import LoginManager
load_dotenv()

username = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
connection_string = f'postgresql://{username}:{password}@{host}:{port}/{db_name}'

# Create a metadata instance

metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_`%(constraint_name)s`",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(metadata=metadata)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.json.compact = True

migrate = Migrate(app, db)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


db.init_app(app)
api = Api(app)
CORS(app)

app.secret_key = os.getenv('SECRET')

bcrypt = Bcrypt(app)

fernet_key = os.getenv('FERNET')

cipher_suite = Fernet(fernet_key)


@login_manager.user_loader
def load_user(user_id):
    from models import User  # Import here to avoid circular import
    return User.query.get(int(user_id))
