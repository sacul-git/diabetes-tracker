import os
from pathlib import Path
import smtplib
import ssl
from base64 import b64encode

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
GMAILUSER = os.environ["GMAILUSER"]
GMAILPASS = os.environ["GMAILPASS"]

connStr = f"postgresql://{PGUSER}:{PGPASS}@{PGHOST}:{PGPORT}/{PGDB}"
connStrLocal = f"postgresql://{PGUSER}:{PGPASS}@0.0.0.0:{PGPORT}/{PGDB}"

db = SQLAlchemy()

class diabUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class confCodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    code = db.Column(db.String(15))


User_tbl = Table('diab_user', diabUser.metadata)
Confcode_tbl = Table('conf_codes', confCodes.metadata)

def create_user_table():
    engine = create_engine(connStr)
    diabUser.metadata.create_all(engine)
    engine.dispose()


def create_conf_table():
    engine = create_engine(connStrLocal)
    confCodes.metadata.create_all(engine)
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


def send_conf_email(recipient_email):
    code = b64encode(os.urandom(6)).decode('utf-8')
    port = 465
    sender = GMAILUSER
    password = GMAILPASS
    context = ssl.create_default_context()
    message = f"Your confirmation code is {code}"
    ins = Confcode_tbl.insert().values(email=recipient_email, code=code)
    engine = create_engine(connStr)
    conn = engine.connect()
    conn.execute(ins)
    conn.close()
    engine.dispose()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient_email, message)


def confirm_code(submitted_code, user_email):
    select_st = select([Confcode_tbl.c.code]) \
            .where(Confcode_tbl.c.email == user_email)
    engine = create_engine(connStr)
    conn = engine.connect()
    rs = conn.execute(select_st)
    if rs.next()[0] == submitted_code:
        return True
    return False

