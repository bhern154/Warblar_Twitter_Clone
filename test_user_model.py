"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler"


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

        # create first test user
        user_1 = User.signup("test1", "email1@email.com", "password", None)
        user_1_id = 1111
        user_1.id = user_1_id

        # create second test user
        user_2 = User.signup("test2", "email2@email.com", "password", None)
        user_2_id = 2222
        user_2.id = user_2_id

        db.session.commit()

        # create self variables to use in other methods
        user_1 = User.query.get(user_1_id)
        user_2 = User.query.get(user_2_id)
        self.user_1 = user_1
        self.user_1_id = user_1_id
        self.user_2 = user_2
        self.user_2_id = user_2_id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_repr_user_model(self):
        """Does the repr method work as expected?"""

        user = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")
        user_id = 50
        user.id = user_id

        db.session.commit()

        self.assertEqual(user.__repr__(), "<User #50: testuser, test@test.com>")

        # User should have no messages & no followers
        # self.assertEqual(len(user.messages), 0)
        # self.assertEqual(len(u.followers), 0)

    ####
    #
    # Following tests
    #
    ####
    def test_user_follows(self):
        self.user_1.following.append(self.user_2)
        db.session.commit()

        self.assertEqual(len(self.user_2.following), 0)
        self.assertEqual(len(self.user_2.followers), 1)
        self.assertEqual(len(self.user_1.followers), 0)
        self.assertEqual(len(self.user_1.following), 1)

        self.assertEqual(self.user_2.followers[0].id, self.user_1.id)
        self.assertEqual(self.user_1.following[0].id, self.user_2.id)

    def test_is_following(self):
        self.user_1.following.append(self.user_2)
        db.session.commit()

        self.assertTrue(self.user_1.is_following(self.user_2))
        self.assertFalse(self.user_2.is_following(self.user_1))

    def test_is_followed_by(self):
        self.user_1.following.append(self.user_2)
        db.session.commit()

        self.assertTrue(self.user_2.is_followed_by(self.user_1))
        self.assertFalse(self.user_1.is_followed_by(self.user_2))

    ####
    #
    # Signup Tests
    #
    ####
    def test_valid_signup(self):
        u_test = User.signup("testtesttest", "testtest@test.com", "password", None)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)
    
    ####
    #
    # Authentication Tests
    #
    ####
    def test_valid_authentication(self):
        u = User.authenticate(self.user_1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.user_1_id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user_1.username, "badpassword"))
