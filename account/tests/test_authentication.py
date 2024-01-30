from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..authentication import EmailAuthBackend


class EmailAuthBackendTest (TestCase):

    def setUp (self):
        # create a test user with a password and an email
        self.user = User.objects.create_user(
            username="Finn",
            password="testpass123",
            email="finn@example.com"
        )
        # create a test client
        self.client = Client()
        # create an instance of your custom backend
        self.backend = EmailAuthBackend()

    def test_authenticate_with_valid_email_and_password(self):
        # authenticate the user with the email and password
        user = self.backend.authenticate(
            request=None,
            username="finn@example.com",
            password="testpass123"
        )
        # assert that the user is not None and is the same as the test user
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_authenticate_with_invalid_email(self):
        # authenticate the user with an invalid email
        user = self.backend.authenticate (
            request=None,
            username="finalin@example.com",
            password="testpass123"
        )
        # assert that the user is None
        self.assertIsNone (user)

    def test_authenticate_with_invalid_password(self):
        # authenticate the user with an invalid password
        user = self.backend.authenticate(
            request=None,
            username="finn@example.com",
            password="testpass678"
        )
        # assert that the user is None
        self.assertIsNone(user)

    def test_get_user_with_valid_user_id(self):
        # get the user with the test user id
        user = self.backend.get_user(self.user.id)
        # assert that the user is not None and is the same as the test user
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_get_user_with_invalid_user_id(self):
        # get the user with an invalid user id
        user = self.backend.get_user(999)
        # assert that the user is None
        self.assertIsNone(user)
