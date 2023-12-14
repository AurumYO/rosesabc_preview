from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.messages import get_messages
from django.urls import reverse

from faker import Faker

from ..forms import UserRegistrationForm, ProfileEditForm, UserEditForm, ProfileEditForm
from ..models import Contact, Profile, Terms
from actions.models import Action


class LoginTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # Create User-follower
        self.follower_user = User.objects.create_user(
            username="Jimmy", email="jimmy@example.com", password="testpass884"
        )
        # Create follow test user record
        Contact.objects.get_or_create(user_from=self.user, user_to=self.follower_user)

    def test_logit_get_request(self):
        # Simulate GET request to login page
        response = self.client.get(reverse("login"))
        # Check if the response status is successful
        self.assertEqual(response.status_code, 200)
        # Check if the response context contains a 'form' for user login
        self.assertIn("form", response.context)
        # Check if coreect form was used for login
        self.assertIsInstance(response.context["form"], AuthenticationForm)

    def test_successful_login(self):
        # Test POST request to the login view with valid credentials
        response = self.client.post(
            reverse("login"), {"username": "Jill", "password": "testpass123"}
        )

        # Check if the response is redirected correctly
        self.assertRedirects(response, reverse("dashboard"))
        # Check if user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_dashboard_page_after_login(self):
        # Log in user
        self.client.login(username="Jill", password="testpass123")

        # Simulate the GET response from the page
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)


class RegisterViewTestCase(TestCase):
    def test_get_request(self):
        # Simulate a GET request to the register view
        response = self.client.get(reverse("register"))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response context contains a 'user_form'
        self.assertIn("user_form", response.context)

        # Check if the 'user_form' in the context is an instance of UserRegistrationForm
        self.assertIsInstance(response.context["user_form"], UserRegistrationForm)

    def test_valid_registration(self):
        # Count the number of users before the test registration
        initial_users_count = User.objects.count()
        # Simulate a POST request to the register view with valid registration data
        user_form = {
            "username": "Jill",
            "first_name": "Jill",
            "email": "jill@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "check_agree_terms_and_services": True,
        }

        response = self.client.post(reverse("register"), user_form)

        # Check if the response is a successful
        self.assertEqual(response.status_code, 200)

        # Check if a new user has been created in the database
        self.assertEqual(User.objects.count(), initial_users_count + 1)
        self.assertTrue(User.objects.filter(username="Jill").exists())

        # Check if a new profile and terms record have been created
        new_user = User.objects.get(username="Jill")
        self.assertTrue(Profile.objects.filter(user=new_user).exists())
        self.assertTrue(Terms.objects.filter(user_id=new_user, is_active=True).exists())

    def test_duplicate_username(self):
        # Create the test user
        self.user = User.objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # Try to create a user with the same name username
        user_form = {
            "username": "Jill",
            "first_name": "Jill",
            "email": "jill@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "check_agree_terms_and_services": True,
        }

        response = self.client.post(reverse("register"), user_form)

        # Check if the response is not a successful redirect
        self.assertTemplateUsed(response, "account/register.html")

    def test_registration_with_invalid_password(self):
        # Try to create a user with the password not matching
        user_form = {
            "username": "Jill",
            "first_name": "Jill",
            "email": "jill@example.com",
            "password": "testpass123",
            "password2": "testpass125",
            "check_agree_terms_and_services": True,
        }
        sign_up_form = UserRegistrationForm(data=user_form)

        # Check if the form data is valid
        form_is_valid = sign_up_form.is_valid()

        # Check if the "password2" field has a ValidationError in its errors
        password2_errors = sign_up_form.errors.get("password2")

        # Use assert to check if the form is not valid and has a ValidationError
        self.assertFalse(form_is_valid)
        self.assertIn("Passwords don't match", password2_errors)



class UserEditTestView(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        Profile.objects.create(user=self.user)

    def test_get_request(self):
        # Simulate login of the user
        self.client.login(username="Jill", password="testpass123")
        # Simulate a GET request to the edit user information
        response = self.client.get(reverse("edit"))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check if the response context contains a "user_form" and "profile_form"
        self.assertIn("user_form", response.context)
        self.assertIn("profile_form", response.context)
        # Check if the "user_form" in the context is an instance of UserEditForm
        self.assertIsInstance(response.context["user_form"], UserEditForm)
        # Check if the "profile_form" in the context is an instance of ProfileEditForm
        self.assertIsInstance(response.context["profile_form"], ProfileEditForm)

    def test_submit_valid_edit_user_form(self):
        self.client.login(username="Jill", password="testpass123")
        form_data = {
            "username": "Jill",
            "first_name": "Jill",
            "email": "jill@example.com",
            "password": "testpass123",
            "about_me": "I am very smart",
            "region": "Galaxy",
        }

        response = self.client.post(reverse("edit"), form_data)
        # Check if the response is a redirect to the dashboard page
        self.assertRedirects(response, reverse("dashboard"))
        # Check if the user's data has been updated in the database
        updated_user = User.objects.get(username="Jill")
        self.assertEqual(updated_user.username, "Jill")
        updated_profile = Profile.objects.get(user=updated_user)
        self.assertEqual(updated_profile.region, "Galaxy")

    def test_form_validation_error(self):
        # Simulate login of the user and submit of invalid data
        self.client.login(username="Jill", password="testpass123")
        invalid_form_data = {
            "username": "Jill",  # Duplicate username
            "email": "invalidemail",  # Invalid email
        }
        response = self.client.post(reverse("edit"), invalid_form_data)

        # Check if the response status code is 200 (OK) since the form data is invalid
        self.assertEqual(response.status_code, 200)

        # Check if error messages are displayed in the response
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Error updating" in str(msg) for msg in messages))

    def test_edit_user_info_with_taken_email(self):
        # Simulate new additional user creation
        self.user2 = User.objects.create_user(
            username="Jimm", email="jimm@example.com", password="testpass123"
        )
        Profile.objects.create(user=self.user2)
        # Simulate login of the user and submit of invalid data
        self.client.login(username="Jill", password="testpass123")
        form_data = {
            "username": "Jill",
            "email": "jimm@example.com",  # Use an email that's already taken
            "region": "Bay",
        }
        response = self.client.post(reverse("edit"), form_data)

        # Check if the response status code is not 200 (OK) due to email conflict
        self.assertEqual(response.status_code, 302)

        # Check if an error message about the email being taken is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Email jimm@example.com already taken." in str(msg) for msg in messages)
        )


class UsersListTestView(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # Create a test user, which doesn't follow any user
        self.user_nonfollower = User.objects.create_user(
            username="Pedro", email="pedro@example.com", password="testpass678"
        )
        # Populate test data base with users
        fake = Faker()
        for u in range(0, 25):
            User.objects.create_user(
                username=fake.name(), email=fake.ascii_safe_email(),\
                    password=fake.password(length=12)
        )
        # Create follow action
        for u in User.objects.all():
            Contact.objects.get_or_create(user_from=self.user, user_to=u)
        
        

    def test_users_listing_view(self):
        # Log in test user
        self.client.login(username="Jill", password="testpass123")
        # Simulate GET request to users_list view
        response = self.client.get(reverse("user_list"))
        # Check if the request response is Ok
        self.assertEqual(response.status_code, 200)
        
        # Check if the filtered actions contain actions related to followed users
        actions = response.context["actions"]
        # filter 2 random users, since test user follows all the users
        u1 = User.objects.filter(id=3)
        u2 = User.objects.filter(id=5)
        for action in actions:
            self.assertIn(action.user, [u1, u2])
        
        # Simulate a GET request to the user_list view with a valid page number
        valid_page_number = 2  # Adjust this to a valid page number
        response = self.client.get(reverse("user_list"), {"page": valid_page_number})

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the users on the requested page match the expected users
        users_on_page = response.context["users"]
        expected_users = User.objects.all()[(valid_page_number - 1) * 12 : valid_page_number * 12]
        self.assertQuerysetEqual(users_on_page, expected_users, transform=lambda x: x)        



    def test_users_listing_view_without_followed_users(self):
        # Log in test user_nonfollower
        self.client.login(username="Pedro", password="testpass678")
        # Simulate GET request to users_list view
        response = self.client.get(reverse("user_list"))
        # Check if the request response is Ok
        self.assertEqual(response.status_code, 200)
        # Check if there are no actions in the context
        actions = response.context.get("actions")
        self.assertQuerysetEqual(actions, [], transform=lambda x: x)

        # Simulate a GET request to the user_list view with an out-of-range page number
        out_of_range_page_number = 1000 
        response = self.client.get(reverse("user_list"), {"page": out_of_range_page_number})

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the users on the page match the users from the last page
        users_on_page = response.context["users"]
        expected_users = User.objects.all()[12 * 2 :]
        self.assertQuerysetEqual(users_on_page, expected_users, transform=lambda x: x)  


class UserDetailsTestView(TestCase):
    def setUp(self):
        # Create a test user
        self.user1 = User.objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # Create another user
        self.user2 = User.objects.create_user(
            username="Pedro", email="pedro@example.com", password="testpass678"
        )
        self.user3 = User.objects.create_user(
            username="Alexandra", email="alexandra@example.com", password="testpass8763"
        )
        # Create follow test user record
        Contact.objects.get_or_create(user_from=self.user1, user_to=self.user2)
        Contact.objects.get_or_create(user_from=self.user1, user_to=self.user3)

    def create_actions(self, user, num_actions):
        for i in range(num_actions):
            Action.objects.create(
                user=user,
                verb=f"action {i}",
                target=user,
            )


    def test_user_detail_view(self):
        # Log in user
        self.client.login(username="Jill", password="testpass123")
        # Simulate GET request to user_detail view
        response = self.client.get(reverse("user_detail", args=[self.user2.username]))
        # Check if the request response is Ok
        self.assertEqual(response.status_code, 200)
        # Check if the filtered actions contain actions related to followed user1
        actions = response.context["actions"]
        print(actions)
        for action in actions:
            self.assertIn(action.user, [self.user2, self.user3])

        
    def test_invalid_user_detail(self):
        # Simulate a GET request to the user_detail view for an invalid user
        response = self.client.get(reverse("user_detail", args=["nonexistentuser"]))

        # Check if the response status code is 302 Redirected to page not found
        self.assertEqual(response.status_code, 302)
