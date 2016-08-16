"""FooDo - A Command Line ToDo App"""
import sys
import traceback
import os
import pwd
import datetime

from collections import defaultdict
from dateutil import tz
from tabulate import tabulate
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship

# Configure SQLite DB
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'foo.db')
sql_alchemy_db_uri = 'sqlite:///' + db_path
# Create core interface to the DB (echo prints SQL statements)
engine = create_engine(sql_alchemy_db_uri, echo=False)
# Use Declarative system - Map python classes to DB tables
Base = declarative_base()
# Create Session (ORMs handle to the the DB)
Session = sessionmaker(bind=engine)
session = Session()

all_headers = ["Id", "Title", "Date", "Status"]

# TODO: Create setup.py

class FooDo(Base):
    __tablename__ = "foodos"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String)

    def __init__(self, title, user_id):
        self.title = title
        self.user_id = user_id
        self.date = datetime.datetime.utcnow()
        self.status = "active"

    def __repr__(self):
        return "<FooDo(id='%s')>" % (self.id)

    @property
    def formatted_date(self):
        # Make naive datetime object time zone aware
        date_aware = self.date.replace(tzinfo=tz.tzutc())
        # Display UTC datetime object in local time zone
        date_aware = date_aware.astimezone(tz.tzlocal())
        return date_aware.strftime("%H:%M %d-%m-%y")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    foodos = relationship("FooDo", backref="user", lazy="dynamic")

    def __init__(self):
        self.id = os.getuid()
        self.name = pwd.getpwuid(os.getuid())[0]

    def __repr__(self):
        return "<User(name='%s')>" % (self.name)

    def list_foodos(self, columns=all_headers, filter_condition=None,
                    order_by_column=FooDo.id):
        query = self.foodos
        if filter_condition is not None:
            query = self.foodos.filter(*filter_condition)
        query = query.order_by(order_by_column)
        results = []
        for foodo in query:
            row = []
            for column in columns:
                if column == "Date":
                    row.append(foodo.formatted_date)
                else:
                    row.append(foodo.__getattribute__(column.lower()))
            results.append(row)
        return results


def add_commit_model(model):
    session.add(model)
    session.commit()


def add_foodo(pargs, user):
    new_foo = FooDo(title=pargs.title, user_id=user.id)
    add_commit_model(new_foo)


def set_foodo(pargs, user):
    foodo = user.foodos.filter(FooDo.id == pargs.id).first()
    if foodo is not None:
        if pargs.complete:
            foodo.status = "complete"
        elif pargs.active:
            foodo.status = "active"
        add_commit_model(foodo)


def delete_foodo(pargs, user):
    foodo = user.foodos.filter(FooDo.id == pargs.id).first()
    if foodo is not None:
        session.delete(foodo)
        session.commit()


def display_table(pargs, table_data):
    table_kwargs = {}
    if pargs.quiet:
        table_kwargs["tablefmt"] = "plain"
    elif pargs.verbose:
        table_kwargs["tablefmt"] = "fancy_grid"
        table_kwargs["headers"] = pargs.columns or all_headers
    else:
        table_kwargs["tablefmt"] = "simple"
        table_kwargs["headers"] = pargs.columns or all_headers
    print tabulate(table_data, **table_kwargs)


def list_foodo(pargs, user):
    list_kwargs = defaultdict(list)
    if pargs.columns:
        list_kwargs["columns"].extend(pargs.columns)
    if pargs.rows:
        list_kwargs["filter_condition"].append(FooDo.id.in_(pargs.rows))
    if pargs.complete:
        list_kwargs["filter_condition"].append(FooDo.status == "complete")
    elif pargs.active:
        list_kwargs["filter_condition"].append(FooDo.status == "active")
    table_data = user.list_foodos(**list_kwargs)
    display_table(pargs, table_data)



def main(pargs):
    try:
        # Create DB Schema (with tables that don't yet exist)
        if not os.path.exists(db_path):
            Base.metadata.create_all(engine)

        user = session.query(User).get(os.getuid())
        if user is None:
            user = User()
            add_commit_model(user)

        pargs.func(pargs, user)
    # TODO: Better Exception handling
    except Exception:
        traceback.print_exc()
        print 'Something went wrong, exiting . . .'
        sys.exit(1)
