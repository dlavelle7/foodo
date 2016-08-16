#!/usr/bin/env python
"""FooDo - A Command Line ToDo App"""
import sys
import traceback
import os
import pwd
import argparse
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


def non_empty_string(value):
    if isinstance(value, str) and value and value.strip():
        return value.strip()
    raise argparse.ArgumentTypeError(
        "%s is an invalid value. Only non empty strings are allowed." % value)


def parse_args():
    parser = argparse.ArgumentParser(description="A command line todo app")
    subparsers = parser.add_subparsers()

    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Add a new FooDo")
    add_parser.add_argument("title", help="New FooDo title",
                            type=non_empty_string)
    add_parser.set_defaults(func=add_foodo)

    # Set subcommand
    set_parser = subparsers.add_parser("set", help="Set status of your FooDo")
    set_parser.add_argument("id", help="Id of FooDo to set", type=int)
    set_group = set_parser.add_mutually_exclusive_group(required=True)
    set_group.add_argument("-c", "--complete", help="Set FooDo complete",
                           action="store_true")
    set_group.add_argument("-a", "--active", help="Set FooDo active",
                           action="store_true")
    set_parser.set_defaults(func=set_foodo)

    delete_parser = subparsers.add_parser("delete", help="Delete a FooDo")
    delete_parser.add_argument("id", help="Id of FooDo to delete", type=int)
    delete_parser.set_defaults(func=delete_foodo)

    # List subcommand
    list_parser = subparsers.add_parser("list", help="List your FooDos")
    list_parser.add_argument("-col", "--columns", choices=all_headers,
            help="FooDo column name(s) you wish to list", type=str, nargs="+")
    list_status_group = list_parser.add_mutually_exclusive_group()
    list_status_group.add_argument("-c", "--complete",
            help="List completed FooDos only", action="store_true")
    list_status_group.add_argument("-a", "--active",
            help="List active FooDos only", action="store_true")
    list_status_group.add_argument("-r", "--rows",
            help="Id(s) of FooDo(s) you wish to list", type=int, nargs="+")
    list_verbosity_group = list_parser.add_mutually_exclusive_group()
    list_verbosity_group.add_argument("-q", "--quiet", help="Quiet mode",
                                      action="store_true")
    list_verbosity_group.add_argument("-v", "--verbose", help="Verbose mode",
                                      action="store_true")
    list_parser.set_defaults(func=list_foodo)
    return parser.parse_args()


def main():
    # Create DB Schema (with tables that don't yet exist)
    if not os.path.exists(db_path):
        Base.metadata.create_all(engine)

    pargs = parse_args()

    user = session.query(User).get(os.getuid())
    if user is None:
        user = User()
        add_commit_model(user)

    pargs.func(pargs, user)


if __name__ == "__main__":
    try:
        main()
    # TODO: Better Exception handling
    except Exception:
        traceback.print_exc()
        print 'Something went wrong, exiting . . .'
        sys.exit(1)
