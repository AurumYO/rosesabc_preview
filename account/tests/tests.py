from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, resolve

from ..forms import UserRegistrationForm
from ..views import register


class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        self.assertEqual(user.username, "Jill")
        self.assertEqual(user.email, "jill@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="superadmin", email="admin@example.com", password="testpass123"
        )
        self.assertEqual(admin_user.username, "superadmin")
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class SignupPageTests(TestCase):
    def setUp(self):
        url = reverse("register")
        self.response = self.client.get(url)

    def test_signup_tempalte(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "account/register.html")
        self.assertContains(self.response, "Sign Up")
        self.assertNotContains(self.response, "Welcome")

    def test_signup_forms(self):
        form = self.response.context.get("user_form")
        self.assertIsInstance(form, UserRegistrationForm)
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_signup_view(self):
        view = resolve("/en/account/register/")
        self.assertEqual(view.func.__name__, register.__name__)


class SignUpTests(TestCase):
    username = "testuser555"
    email = "testuser555@example.com"

    def setUp(self):
        url = reverse("login")
        self.response = self.client.get(url)

    def test_signup_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "registration/login.html")
        self.assertContains(self.response, "Log In")
        self.assertNotContains(self.response, "Hi there, Signin in please!")

    def test_signup_form(self):
        new_user = get_user_model().objects.create_user(self.username, self.email)
        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertEqual(get_user_model().objects.all()[0].username, self.username)
        self.assertEqual(get_user_model().objects.all()[0].email, self.email)
