import os
import pwd
import datetime

from dateutil import tz
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

# Use Declarative system - Map python classes to DB tables
Base = declarative_base()
all_headers = ["Id", "Title", "Date", "Status"]


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
