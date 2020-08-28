import os
from pathlib import Path
import smtplib
import ssl
from base64 import b64encode

from sqlalchemy import Table, create_engine, MetaData, Column, Integer, String, Float, DateTime
from sqlalchemy.sql import select
from sqlalchemy.schema import CreateSchema
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import pandas as pd
import ohio.ext.pandas

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
userdata_metadata = MetaData()

# table definitions
## user management tables

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


def create_tables() -> None:
    """
    Create the username/password (users) and confirmation code (conf_codes)
    Postgresql tables

    Returns None
    """
    engine = create_engine(connStr)
    db.Model.metadata.create_all(engine)
    engine.dispose()

## data tables
def create_basic_tracker_table(schema: str) -> None:
    """
    Create the mysugr data (basic_tracker) Postgresql table within the given
    schema

    Returns None
    """
    engine = create_engine(connStr)
    # meta = MetaData()
    meta = userdata_metadata
    basicTracker = Table(
        "basic_tracker", meta,
        Column("entryid", Integer, primary_key=True),
        Column("date", String(20)),
        Column("time", String(20)),
        Column("tags", String(50)),
        Column("blood_sugar", Float),
        Column("insulin_injection_pen_units", Float),
        Column("insulin_injection_basal_units", Float),
        Column("insulin_injection_pump_units", Float),
        Column("insulin_meal", Float),
        Column("insulin_correction", Float),
        Column("temporary_basal_percentage", Float),
        Column("temporary_basal_duration", Float),
        Column("meal_carbohydrates", Float),
        Column("meal_descriptions", Float),
        Column("activity_duration", Float),
        Column("activity_intensity", Float),
        Column("activity_description", Float),
        Column("steps", Float),
        Column("note", String(150)),
        Column("location", Float),
        Column("blood_pressure", String(10)),
        Column("body_weight", Float),
        Column("hba1c", Float),
        Column("ketones", Float),
        Column("food_type" ,Float),
        Column("medication" ,Float),
        schema = schema
        )
    basicTracker.create(engine)
    engine.dispose()


def upload_sugr_data(path: str, schema: str) -> None:
    """
    Uploads data from mySugr app to Postgres. Uses all of the columns provided
    in mySugr data export csv (some of which are probably not needed)

    Args:
        path (str): Path to mySugar export csv

    Returns:
        None
    """
    engine = create_engine(connStr)
    tbl = Table("basic_tracker", userdata_metadata, autoload_with=engine, schema=schema)
    columns = [c.name for c in tbl.c][1:]
    # check existing:
    postgresdf = pd.DataFrame.pg_copy_from(
            "basic_tracker",
            engine,
            schema=schema,
            columns = columns
        )
    # import new mySugr
    exportdf = pd.read_csv(path, names = postgresdf.columns, header=0, index_col = None)
    #combine the two, keep the original values from postgresdf
    df = pd.concat([postgresdf, exportdf]).drop_duplicates(keep="first")
    df.pg_copy_to(
        name = "basic_tracker",
        schema = schema,
        con = engine,
        if_exists = "replace",
        index = True
    )
    return

# User management utils

def add_user(username, password, email):
    """
    Add a user to the username / password database and create a schema for them

    Args:
        username (str): the username you want to add to the database
        password (str): the username's password
        email (str): the user's email

    Returns:
        None
    """
    hashed_password = generate_password_hash(password, method='sha256')
    ins = db.Model.metadata.tables["diab_user"].insert().values(
        username=username, email=email, password=hashed_password)
    engine = create_engine(connStr)
    conn = engine.connect()
    conn.execute(ins)
    # create a schema for each user and add tables
    engine.execute(CreateSchema(username))
    create_basic_tracker_table(username)
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
    delete = db.Model.metadata.tables["diab_user"].delete().where(db.Model.metadata.tables["diab_user"].c.username == username)
    engine = create_engine(connStr)
    conn = engine.connect()
    conn.execute(delete)
    conn.execute(f"DROP SCHEMA IF EXISTS {username} CASCADE;")
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


# db query tools
def execute_query(
        query: str = "",
        query_file: None = None,
        return_ResultProxy: bool = False
):
    """
    Executes a query, either from a string or a .sql file
    You will need to have a tunnel to the database server running.

    Args:
        query (str): The query to be executed
            Either query or query_file must be supplied
        query_file (str): path to a .sql file containing the query to run.
            Either query or query_file must be supplied
        return_ResultProxy (bool): Whether to return an
            sqlalchemy.engine.result.ResultProxy instead of a pandas dataframe
            Defaults to False (i.e. return a pd.DataFrame by default)

    Returns:
        pandas.DataFrame or sqlalchemy.engine.result.ResultProxy

    """
    engine = create_engine(connStr)
    if query == "":
        try:
            with open(query_file, "r") as f:
                query = f.read()
        except TypeError:
            raise TypeError("No query found, did you supply either a query or a sql file?")
        except FileNotFoundError as e:
            raise e
    with engine.connect() as connection:
        if return_ResultProxy:
            query_results = connection.execute(query)
        else:
            query_results = pd.read_sql_query(query, connection)
    return query_results



