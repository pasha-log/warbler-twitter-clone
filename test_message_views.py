"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
        # Message.query.delete()

        db.drop_all() 
        db.create_all() 

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    header_image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            response = client.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(response.status_code, 302)

            msg = Message.query.first()
            self.assertEqual(msg.text, "Hello")

    def test_delete_message(self):
        """When you are logged in, can you delete a message as yourself?""" 

        msg1 = Message(id='7676', text="Hi", user_id=self.testuser.id)
        db.session.add(msg1)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser.id

            response = client.post('/messages/7676/delete', follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            msg = Message.query.get(7676)

            self.assertIsNone(msg)
    
    def test_logged_out_adding_message(self):
        """When you’re logged out, are you prohibited from adding messages?"""

        with self.client as client:
            response = client.post("/messages/new", data={"text": "Hi there"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

    def test_logged_out_delete_message(self):
        """When you are logged out, are you prohibited from deleting messages?""" 

        msg2 = Message(id='8686', text="Hello there stranger", user_id=self.testuser.id)
        db.session.add(msg2)
        db.session.commit()

        with self.client as client:
            response = client.post('/messages/8686/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

    def test_add_message_as_another_user(self):
        """When you are logged in, are you prohibiting from adding a message as another user?""" 

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = 95639 # user does not exist

            response = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

    def test_delete_other_user_message(self):
        """When you are logged in, are you prohibiting from deleting a message as another user?"""

        msg3 = Message(id='9696', text="Hello there stranger", user_id=self.testuser.id)
        db.session.add(msg3)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = 95639 

            response = client.post('/messages/9696/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

            

            