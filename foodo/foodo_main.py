"""FooDo - A Command Line ToDo App"""
import sys
import os
import argparse

from collections import defaultdict
from tabulate import tabulate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure SQLite DB
basedir = os.path.abspath('/var/lib/foodo')
db_path = os.path.join(basedir, 'foodo.db')
sql_alchemy_db_uri = 'sqlite:///' + db_path
# Create core interface to the DB (echo prints SQL statements)
engine = create_engine(sql_alchemy_db_uri, echo=False)
# Create Session (ORMs handle to the the DB)
Session = sessionmaker(bind=engine)
session = Session()

from foodo.models import FooDo, User, Base, all_headers


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
    try:
        # Create DB Schema (with tables that don't yet exist)
        if not os.path.exists(basedir):
            os.mkdir(basedir)
            Base.metadata.create_all(engine)

        user = session.query(User).get(os.getuid())
        if user is None:
            user = User()
            add_commit_model(user)

        pargs = parse_args()
        pargs.func(pargs, user)
    # TODO: Better Exception handling
    except Exception as exception:
        print exception
        print 'Something went wrong, exiting . . .'
        sys.exit(1)
