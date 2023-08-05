import unittest
import sys
sys.path[0:0] = [""]

from mongoengine import *
from mongoengine.connection import get_db
from mongoengine.queryset import transform
from datetime import datetime, timedelta
from bson import SON

__all__ = ("DynamicTest", )


class DynamicTest(unittest.TestCase):

    def setUp(self):
        connect(db='mongoenginetest')
        self.db = get_db()

    def test_nested_nested_fields_mark_as_changed(self):

        class Simple(Document):
            x = ListField()

        Simple.drop_collection()

if __name__ == '__main__':
    unittest.main()
