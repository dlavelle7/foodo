import unittest
import foodo

from argparse import ArgumentTypeError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


class Test(unittest.TestCase):

    def setUp(self):
        # Create in memory SQLite DB for UTs (empty URL)
        engine = create_engine('sqlite://')
        Session = sessionmaker(bind=engine)
        self.session = Session()
        foodo.Base.metadata.create_all(engine)

    def tearDown(self):
        pass

    def test_non_empty_string(self):
        # Assert the Foodo title field accepts (and strips) non empty strings
        self.assertRaises(ArgumentTypeError, foodo.non_empty_string, '')
        self.assertRaises(ArgumentTypeError, foodo.non_empty_string, ' ')
        self.assertRaises(ArgumentTypeError, foodo.non_empty_string, None)
        self.assertRaises(ArgumentTypeError, foodo.non_empty_string, 12)

        self.assertEquals('a', foodo.non_empty_string('  a'))
        self.assertEquals('b', foodo.non_empty_string('b  '))
        self.assertEquals('.', foodo.non_empty_string(' . '))
        self.assertEquals('123', foodo.non_empty_string(' 123 '))

    def test_list_columns_with_date(self):
        user = foodo.User()
        self.session.add(user)
        foo = foodo.FooDo('Test', user.id)
        self.session.add(foo)
        self.session.commit()

        # Assert that a string formatted date is return when querying columns
        result = user.list_foodos(['Date'])
        # 1 FooDo with 1 column queried
        self.assertEquals(1, len(result))
        self.assertEquals(1, len(result[0]))
        # String not datetime object
        self.assertEquals(str, type(result[0][0]))

    # TODO: More UTs
