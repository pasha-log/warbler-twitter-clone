"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase

from sqlalchemy.exc import IntegrityError

from models import db, User, Message, Follows

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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()
        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        u = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png",
            header_image_url="/static/images/warbler-hero.jpg"
        )

        uid = 0000
        u.id = uid

        u1 = User.signup(
            username="test1", 
            email="email1@email.com", 
            password="password", 
            image_url="/static/images/default-pic.png",
            header_image_url="/static/images/warbler-hero.jpg"
        )

        uid1 = 1111
        u1.id = uid1

        u2 = User.signup(
            username="testuser2",
            email="test2@test2.com",
            password="HASHED_PASSWORD2",
            image_url="/static/images/default-pic.png",
            header_image_url="/static/images/warbler-hero.jpg"
        )

        uid2 = 2222
        u2.id = uid2

        u3 = User.signup(
            username="testuser3", 
            email="test3@test3.com",
            password="HASHED_PASSWORD3",
            image_url="/static/images/default-pic.png",
            header_image_url="/static/images/warbler-hero.jpg"
        )

        uid3 = 3333
        u3.id = uid3

        db.session.commit()

        u = User.query.get(uid)
        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)
        u3 = User.query.get(uid3)

        self.u = u 
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3 

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        """Does the repr method work as expected?"""

        self.assertEqual(repr(u), f"<User #{u.id}: testuser, test@test.com>")

#########################################################
# TESTING FOLLOWING 
#########################################################

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""

        u.following.append(u2)
        
        self.assertEqual(u.is_following(u2), 1)

        # Does is_following successfully detect when user1 is not following user2?
        u.following.remove(u2)
        db.session.commit()
        self.assertEqual(u.is_following(u2), 0)

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""

        u.followers.append(u2)

        db.session.commit()
        self.assertEqual(u.is_followed_by(u2), 1)

        # Does is_followed_by successfully detect when user1 is not followed by user2?
        u.followers.remove(u2)
        db.session.commit()
        self.assertEqual(u.is_followed_by(u2), 0)

########################################################
# TESTING SIGNING UP
########################################################

    def test_valid_user_signup(self):
        """Does User.signup successfully create a new user given valid credentials?"""

        self.assertTrue(isinstance(u3.id, int))

        # Does User.signup fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
        with self.assertRaises(IntegrityError):
            u4 = User.signup(username="testuser", 
            password="HASHED_PASSWORD4",
            email="test4@test4.com",
            image_url="/static/images/default-pic.png",
            header_image_url="/static/images/warbler-hero.jpg"
            )
            db.session.commit()

        with self.assertRaises(ValueError): 
            u5 = User.signup(username="", 
            password="",
            email="",
            image_url="",
            header_image_url=""
            )
            db.session.commit()

#########################################################
# TESTING AUTHENTICATION
#########################################################

    def test_valid_authentication(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        # u1 = User.signup("test1", "email1@email.com", "password", None, None)
        # uid1 = 1111
        # u1.id = uid1
        # u1 = User.query.get(uid1)
        # self.u1 = u1
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)

        self.assertEqual(u.id, self.uid1)
    
    def test_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""

        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""

        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))

