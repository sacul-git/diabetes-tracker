import os
from pathlib import Path

from sqlalchemy import Table, create_engine
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

env_path = Path('.') / '.secrets.env'
load_dotenv(dotenv_path=env_path)

PGHOST = os.environ["PGHOST"]
PGUSER = os.environ["PGUSER"]
PGPASS = os.environ["PGPASS"]
PGPORT = os.environ["PGPORT"]
PGDB = os.environ["PGDB"]

connStr = f"postgresql://{PGUSER}:{PGPASS}@{PGHOST}:{PGPORT}/{PGDB}"

db = SQLAlchemy()

class diabUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

User_tbl = Table('diab_user', diabUser.metadata)

def create_user_table():
    engine = create_engine(connStr)
    diabUser.metadata.create_all(engine)
    engine.dispose()

def add_user(username, password, email):
    hashed_password = generate_password_hash(password, method='sha256')
    ins = User_tbl.insert().values(username=username, email=email, password=hashed_password)
    engine = create_engine(connStr)
    conn = engine.connect()
    conn.execute(ins)
    conn.close()
    engine.dispose()

def del_user(username):
    delete = User_tbl.delete().where(User_tbl.c.username == username)
    engine = create_engine(connStr)
    conn = engine.connect()
    conn.execute(delete)
    conn.close()
    engine.dispose()


def show_users():
    select_st = select([User_tbl.c.username, User_tbl.c.email])
    engine = create_engine(connStr)
    conn = engine.connect()
    rs = conn.execute(select_st)
    for row in rs:
        print(row)
    conn.close()
    engine.dispose()

