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
import pandas as pd

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

# table definitions
## user creation and management

class diabUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


class confCodes(db.Model):
    __tablename__ = "conf_codes"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    code = db.Column(db.String(15))


## data tables
class basicTracker(db.Model):
    __tablename__ = "basic_tracker"
    entryid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    tags = db.Column(db.String(50))
    blood_sugar = db.Column(db.Float)
    insulin_injection_pen_units = db.Column(db.Float)
    insulin_injection_basal_units = db.Column(db.Float)
    insulin_injection_pump_units = db.Column(db.Float)
    insulin_meal = db.Column(db.Float)
    insulin_correction = db.Column(db.Float)
    temporary_basal_percentage = db.Column(db.Float)
    temporary_basal_duration = db.Column(db.Float)
    meal_carbohydrates = db.Column(db.Float)
    meal_descriptions = db.Column(db.Float)
    activity_duration = db.Column(db.Float)
    activity_intensity = db.Column(db.Float)
    activity_description = db.Column(db.Float)
    steps = db.Column(db.Float)
    note = db.Column(db.String(150))
    location = db.Column(db.Float)
    blood_pressure = db.Column(db.String(10))
    body_weight = db.Column(db.Float)
    hba1c = db.Column(db.Float)
    ketones = db.Column(db.Float)
    food_type = db.Column(db.Float)
    medication = db.Column(db.Float)


def create_tables() -> None:
    """
    Create the username/password (users), confirmation code (conf_codes) and
    mysugr data (basic_tracker) Postgresql tables

    Returns None
    """
    engine = create_engine(connStr)
    db.Model.metadata.create_all(engine)
    engine.dispose()


def upload_sugr_data(path: str) -> None:
    """
    Uploads data from mySugr app to Postgres. Uses all of the columns provided
    in mySugr data export csv (some of which are probably not needed)

    Args:
        path (str): Path to mySugar export csv

    Returns:
        None
    """
    engine = create_engine(connStr)
    columns = db.Model.metadata.tables["basic_tracker"].columns.keys()[1:]
    df = pd.read_csv(path, names = columns, header = 1)
    df.to_sql(
        name = "basic_tracker",
        con = engine,
        if_exists = "append",
        index = False
    )

# User management utils

def add_user(username, password, email):
    hashed_password = generate_password_hash(password, method='sha256')
    ins = db.Model.metadata.tables["users"].insert().values(
        username=username, email=email, password=hashed_password)
    engine = create_engine(connStr)
    conn = engine.connect()
    conn.execute(ins)
    conn.close()
    engine.dispose()


def del_user(username: str) -> None:
    """
    Delete a user from the username / password database

    Args:
        username (str): the username you want to delete from the database

    Returns:
        None
    """
    delete = db.Model.metadata.tables["users"].delete().where(db.Model.metadata.tables["users"].c.username == username)
    engine = create_engine(connStr)
    conn = engine.connect()
    conn.execute(delete)
    conn.close()
    engine.dispose()


def send_conf_email(recipient_email: str) -> None:
    """
    Sends a confirmation code for registration. Requires GMAILUSER and
    GMAILPASS environment variables, pointing to a gmail account for which the
    "Allow less secure apps" setting is turned ON

    Args:
        recipient_email (str): the email address to send the confirmation code
            to

    Returns:
        None

    """
    code = b64encode(os.urandom(6)).decode('utf-8')
    port = 465
    sender = GMAILUSER
    password = GMAILPASS
    context = ssl.create_default_context()
    message = f"Your confirmation code is {code}"
    ins = db.Model.metadata.tables["conf_codes"].insert().values(email=recipient_email, code=code)
    engine = create_engine(connStr)
    conn = engine.connect()
    conn.execute(ins)
    conn.close()
    engine.dispose()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient_email, message)


def confirm_code(submitted_code, user_email):
    select_st = select([db.Model.metadata.tables["conf_codes"].c.code]) \
        .where(db.Model.metadata.tables["conf_codes"].c.email == user_email)
    engine = create_engine(connStr)
    conn = engine.connect()
    rs = conn.execute(select_st)
    if rs.next()[0] == submitted_code:
        return True
    return False
