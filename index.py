import logging
import os
from pathlib import Path

from flask_login import LoginManager, UserMixin

from app import app
from users_utils import db, connStr
from layouts.app_layout import serve_layout
import callbacks
from callbacks import User

server = app.server

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

app.layout = serve_layout

default_key = os.urandom(12)

server.config.update(
    SECRET_KEY=os.getenv("FLASKMOHMALIKEY", default_key),
    SQLALCHEMY_DATABASE_URI=connStr,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(server)

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    # app.run_server(debug=True, port=5017, host='0.0.0.0')
    context = ('cert.pem', 'key.pem') #certificate and key files
    # context = "adhoc"
    app.run_server(debug=True, port=5017, host='0.0.0.0', ssl_context=context)
