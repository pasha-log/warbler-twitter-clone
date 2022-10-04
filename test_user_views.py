import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY
 
db.create_all()  

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase): 
    """Tests for views for Users.""" 

    def setUp(self): 
        """Create test client, add sample data.""" 

        db.drop_all() 
        db.create_all() 

        self.client = app.test_client()

        u = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png",
            header_image_url="/static/images/warbler-hero.jpg"
        )

        uid = 4242
        u.id = uid

        u1 = User.signup(
            username="testuser1",
            email="test1@test1.com",
            password="HASHED_PASSWORD1",
            image_url="/static/images/default-pic.png",
            header_image_url="/static/images/warbler-hero.jpg"
        )

        uid1 = 1111
        u1.id = uid1

        u2 = User.signup(
            username="lmnop",
            email="test2@test2.com",
            password="HASHED_PASSWORD2",
            image_url=None,
            header_image_url=None
        )

        uid2 = 2222
        u2.id = uid2

        m = Message(
            text='testing message', 
            user_id=u.id
        )

        mid = 3333
        m.id = mid

        db.session.add_all([u, u1, m])
        db.session.commit()

        u = User.query.get(uid)
        u1 = User.query.get(uid1)
        m = Message.query.get(mid)

        self.u = u 
        self.uid = uid

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.m = m
        self.mid = mid

        self.u.followers.append(self.u1)
        self.u.following.append(self.u1)

        db.session.commit()

    def tearDown(self): 
        """Clean up any fouled transaction.""" 
        
        res = super().tearDown()
        db.session.rollback()
        return res 

########################################################
# TEST FOLLOWS
########################################################

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.uid, user_following_id=self.uid1)
        f2 = Follows(user_being_followed_id=self.uid1, user_following_id=self.uid)

        db.session.add_all([f1, f2])
        db.session.commit()

    def test_user_view_with_follows(self):
        # self.setup_followers()
        with self.client as client:
            response = client.get(f"/users/{self.uid}")

            self.assertEqual(response.status_code, 200)

            self.assertIn("@testuser", str(response.data))
            soup = BeautifulSoup(str(response.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 0 messages
            self.assertIn("1", found[0].text)

            # Test for a count of 1 following
            self.assertIn("1", found[1].text)

            # Test for a count of 1 follower
            self.assertIn("1", found[2].text)

            # Test for a count of 0 likes
            self.assertIn("0", found[3].text)

# When you’re logged in, can you see the follower / following pages for any user?
    def test_view_following(self):
        # self.setup_followers()
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.uid

            response = client.get(f"/users/{self.uid}/following")
            self.assertEqual(response.status_code, 200)
            self.assertIn("@testuser1", str(response.data))
            self.assertNotIn("@lmnop", str(response.data))
        

    def test_view_followers(self):
        # self.setup_followers()
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.uid

            response = client.get(f"/users/{self.uid}/followers")
            self.assertEqual(response.status_code, 200)
            self.assertIn("@testuser1", str(response.data))
            self.assertNotIn("@lmnop", str(response.data))

# When you’re logged out, are you disallowed from visiting a user’s follower / following pages?
    def test_unauthorized_following_page_access(self):
        # self.setup_followers()
        with self.client as client:

            response = client.get(f"/users/{self.uid}/following", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("@testuser1", str(response.data))
            self.assertIn("Access unauthorized", str(response.data))

    def test_unauthorized_followers_page_access(self):
        # self.setup_followers()
        with self.client as client:

            response = client.get(f"/users/{self.uid}/followers", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("@testuser1", str(response.data))
            self.assertIn("Access unauthorized", str(response.data))

##########################################################
# TEST SEARCH FOR USERS
##########################################################

    def test_search_users(self):
        with self.client as client:
            response = client.get("/users?q=test")

            self.assertIn("@testuser", str(response.data))
            self.assertIn("@testuser1", str(response.data))            
            self.assertNotIn("@lmnop", str(response.data))
        
##########################################################
# TEST LIKES
##########################################################

    def setup_likes(self):
        msg1 = Message(text="something crazy happened", user_id=self.uid)
        msg2 = Message(text="We have a new baby", user_id=self.uid)
        msg3 = Message(id=9999, text="likable content", user_id=self.uid1)
        db.session.add_all([msg1, msg2, msg3])
        db.session.commit()

        l1 = Likes(user_id=self.uid, message_id=9999)

        db.session.add(l1)
        db.session.commit()

    def test_user_view_with_likes(self):
        self.setup_likes()
        with self.client as client:
            response = client.get(f"/users/{self.uid}")

            self.assertEqual(response.status_code, 200)

            self.assertIn("@testuser", str(response.data))
            soup = BeautifulSoup(str(response.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("3", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("1", found[1].text)

            # Test for a count of 0 following
            self.assertIn("1", found[2].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)

    def test_add_like(self):
        msg4 = Message(id=1945, text="I hate flat-earthers", user_id=self.uid1)
        db.session.add(msg4)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.uid

            resp = client.post("/messages/1945/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==1945).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.uid)

    def test_remove_like(self):
        self.setup_likes()
        msg3 = Message.query.filter(Message.text=="likable content").one()
        self.assertIsNotNone(msg3)
        self.assertNotEqual(msg3.user_id, self.uid)

        like = Likes.query.filter(
            Likes.user_id==self.uid and Likes.message_id==msg3.id
        ).one()

        # Now we are sure that testuser likes the message "likable content"
        self.assertIsNotNone(like)

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.uid

            response = client.post(f"/messages/{msg3.id}/like", follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==msg3.id).all()
            # the like has been deleted
            self.assertEqual(len(likes), 0)

