"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# test_if_valid_message
# test_user_id_of_message 
# test_message_in_user_messages
db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()

        u = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png",
            header_image_url="/static/images/warbler-hero.jpg"
        )

        uid = 0000
        u.id = uid

        m = Message(
            text='testing message', 
            timestamp=datetime.utcnow(), 
            user_id=u.id
        )

        mid = 1111
        m.id = mid

        db.session.add_all([u, m])
        db.session.commit()

        u = User.query.get(uid)
        m = Message.query.get(mid)

        self.u = u 
        self.uid = uid

        self.m = m
        self.mid = mid

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        # User should have one messages
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, 'testing message')

    def test_repr_method(self):
        """Does the repr method work as expected?"""

        self.assertEqual(repr(self.m), f"<Message #{self.mid}, {self.m.text}, {self.m.timestamp}, {self.uid}>")

    def test_valid_message_creation(self):
        """Does Message successfully create a new user given valid credentials?"""

        self.assertEqual(self.mid, 1111)
        self.assertNotEqual(self.mid, 7777)
        self.assertEqual(self.m.user_id, 0000)

        self.assertIsNotNone(self.m)
        self.assertEqual(self.m.text, "testing message")
        self.assertEqual(self.m.user_id, self.uid)

    def test_message_likes(self):
        m1 = Message(
            text="a warble",
            user_id=self.uid
        )

        u2 = User.signup("yetanothertest", "t@email.com", "password", None, None)
        uid2 = 888
        u2.id = uid2
        db.session.add_all([m1, u2])
        db.session.commit()

        u2.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid2).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m1.id)

