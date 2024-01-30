import os
from django.conf import settings
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages import get_messages
from django.core.paginator import Paginator
from django.urls import reverse

from faker import Faker

from ..views import user_unfollow
from ..forms import LoginForm, UserRegistrationForm, ProfileEditForm, UserEditForm, ProfileEditForm
from ..models import Contact, Profile, Terms
from roses.models import Rose, RosePhoto, RoseYoutubeVideo
from library.models import Article, Issue, ArticleCategory, Plant
from actions.models import Action
from library.tests.test_views import create_plant_data, create_issue_type_data, create_article_category_data, create_article_data
from roses.tests.test_views import create_rose_objects, create_rose_pic_objects, create_rose_video_objects

fake = Faker()


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

    def test_login_get_request(self):
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
        
        # Simulate a GET request to the user_list view with a valid page number
        valid_page_number = 2  # Adjust this to a valid page number
        response = self.client.get(reverse("user_list"), {"page": valid_page_number})

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the users on the requested page match the expected users
        users_on_page = response.context["users"]
        expected_users = User.objects.all().order_by('username')\
            [(valid_page_number - 1) * 12 : valid_page_number * 12]
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
        expected_users = User.objects.all().order_by('username')[12 * 2 :]
        self.assertQuerysetEqual(users_on_page, expected_users, transform=lambda x: x)


class UserFollowTestCase(TestCase):
    """
    Test case for user following functionality.

    Tests are focused on the 'user_follow' view, which allows users to follow each other.

    Attributes:
        user1 (User): The first test user.
        user2 (User): The second test user.
        client (Client): Django test client used for making requests in tests.

    Methods:
        setUp(): Prepare necessary data and log in the first test user.
        test_user_follow(): Test user following functionality with a valid user.
        test_user_follow_unexisting_user(): Test user following with an invalid (nonexistent) user.
        tearDown(): Log out the currently logged-in user after each test.
    """
    def setUp(self):
        """
        Prepare necessary data and log in the first test user.
        """
        self.user1 = User.objects.create_user(username='Jill', password='testpass123')
        self.user2 = User.objects.create_user(username='Sam', password='testpass123')
        self.client.login(username='Jill', password='testpass123')

    def test_user_follow(self):
        """
        Test user following functionality with a valid user.

        1. Make a POST request to follow the second test user.
        2. Assert that the response status code is 302 (redirect).
        3. Assert that a Contact object is created, indicating that the first user is following the second user.
        """
        response = self.client.post(reverse('user_follow', args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contact.objects.filter(user_from=self.user1, user_to=self.user2).exists())

    def test_user_follow_unexisting_user(self):
        """
        Test user following with an invalid (nonexistent) user.

        1. Make a POST request to follow a nonexistent user (ID 100).
        2. Assert that the response status code is 200 (OK).
        3. Assert that the response JSON content indicates an error status.
        """
        response = self.client.post(reverse('user_follow', args=[100]))
        # HTTP response status code that will be returned if the User.DoesNotExist exception is raised is 200 OK 1
        self.assertEqual(response.status_code, 200)
        # check that the exception is raised and user does not exists
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'status': 'error'})

    def tearDown(self):
        """
        Log out the currently logged-in user after each test.
        """
        self.client.logout()


class UserUnfollowTestCase(TestCase):
    """
    Test case for user unfollowing functionality.

    Tests are focused on the 'user_unfollow' view, which allows users to unfollow each other.

    Attributes:
        user1 (User): The first test user.
        user2 (User): The second test user.
        client (Client): Django test client used for making requests in tests.

    Methods:
        setUp(): Prepare necessary data and log in the first test user.
        test_user_unfollow(): Test user unfollowing functionality with a valid user.
        test_user_unfollow_unexisting_user(): Test user unfollowing with an invalid (nonexistent) user.
        tearDown(): Log out the currently logged-in user after each test.
    """
    def setUp(self):
        """
        Prepare necessary data and log in the first test user.
        """
        self.user1 = User.objects.create_user(username='Jill', password='testpass123')
        self.user2 = User.objects.create_user(username='Sam', password='testpass123')
        self.client.login(username='Jill', password='testpass123')

    def test_user_unfollow(self):
        """
        Test user unfollowing functionality with a valid user.

        1. Make a POST request to unfollow the second test user.
        2. Assert that the response status code is 302 (redirect).
        3. Assert that a Contact object is deleted, indicating that the first user unfollowed the second user.
        """
        response = self.client.post(reverse('user_unfollow', args=[self.user2.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Contact.objects.filter(user_from=self.user1, user_to=self.user2).exists())

    def test_user_unfollow_unexisting_user(self):
        """
        Test user unfollowing with an invalid (nonexistent) user.

        1. Make a POST request to unfollow a nonexistent user (ID 100).
        2. Assert that the response status code is 200 (OK).
        3. Assert that the response JSON content indicates an error status.
        """
        response = self.client.post(reverse('user_unfollow', args=[100]))
        # HTTP response status code that will be returned if the User.DoesNotExist exception is raised is 200 OK 1
        self.assertEqual(response.status_code, 200)
        # check that the exception is raised and user does not exists
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'status': 'error'})

    def tearDown(self):
        """
        Log out the currently logged-in user after each test.
        """
        self.client.logout()


class UserDeleteAccountPageTestView(TestCase):
    """
    Test case for user redirected to delete account page functionality.

    Tests are focused on the 'delete_page' view, which allows users to go to 'delete account' page.

    Attributes:
        user (User): The test user.
        client (Client): Django test client used for making requests in tests.

    Methods:
        setUp(): Prepare necessary data and log in the test user.
        test_user_delete_page(): Test user go to delete page functionality.
        tearDown(): Log out after each test.
    """
    def setUp(self):
        """
        Prepare necessary data and log in the test user.
        """
        self.user = User.objects.create_user(username='Jill', password='testpass123')
        self.client.login(username='Jill', password='testpass123')

    def test_user_delete_page(self):
        """
        Go to delete account page without deleting the user account from data base
        """
        response = self.client.post(reverse('delete_page'))
        self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        """
        Log out the currently logged-in user after each test.
        """
        self.client.logout()


class UserDeleteAccountTestView(TestCase):
    """
    Test case for user redirected to delete account functionality.

    Tests are focused on the 'delete_account' view, which allows users to go to delete account.

    Attributes:
        user (User): The test user.
        profile: The profile of the user
        client (Client): Django test client used for making requests in tests.

    Methods:
        setUp(): Prepare necessary data and log in the test user.
        test_user_delete_account(): Test user go to delete account functionality and delete the 
                                    account and profile.
        test_user_delete_account_user_DoesNotExists(): Test to delete the unexistent user 
        tearDown(): Log out after each test.
    """
    def setUp(self):
        """
        Prepare necessary data and log in the test user.
        """
        self.user = User.objects.create_user(username='Jill', password='testpass123')
        self.profile = Profile.objects.create(user=self.user)
        self.client.login(username='Jill', password='testpass123')

    def test_user_delete_account(self):
        # Check if user is in database
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertTrue(User.objects.filter(id=self.user.id).exists())
        response = self.client.post(reverse('delete_account'))
        # Check if profile and user account was deleted from database
        self.assertFalse(Profile.objects.filter(user=self.user).exists())
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
        # check if the user was correctly redirected to Home page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your account and all credentials were successfully deleted.")
        self.assertTemplateUsed(response, "roses/home.html")

    def test_user_delete_account_user_DoesNotExists(self):
        # delete user's proile and user from database
        self.profile.delete()
        self.user.delete()
        # Try to access the delete account view
        response = self.client.get(reverse("delete_account"))
        # Assert that a User.DoesNotExist exception is raised
        self.assertRaises(User.DoesNotExist)
        # Assert that the response status code is 302
        self.assertEqual(response.status_code, 302)
        # Assert that the response contains an error message

    def tearDown(self):
        self.client.logout()
    

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

    def test_user_detail_view(self):
        # Log in user
        self.client.login(username="Jill", password="testpass123")
        # Simulate GET request to user_detail view
        response = self.client.get(reverse("user_detail", args=[self.user2.username]))
        # Check if the request response is Ok
        self.assertEqual(response.status_code, 200)
        
    def test_invalid_user_detail(self):
        # Simulate a GET request to the user_detail view for an invalid user
        response = self.client.get(reverse("user_detail", args=["nonexistentuser"]))

        # Check if the response status code is 302 Redirected to page not found
        self.assertEqual(response.status_code, 302)


class LikedRosesTest(TestCase):
    def setUp(self):
        # Create a user and a profile for testing
        self.user = User.objects.create_user(username="Sam", password="testpass123")
        self.profile = Profile.objects.create(user=self.user)
        # Create some roses data for testing
        self.roses = create_rose_objects(50, self.user)
        self.liked_roses = self.user.roses_liked.filter(translations__language_code="en")\
            .order_by("translations__name")
        self.paginator = Paginator(self.liked_roses, 20)
        # Make the user like some roses for testing
        # self.user.roses_liked.add(*self.roses[:10])
        # Create some other users and actions for testing
        self.other_users = [User.objects.create_user(username=f"user{i}", password=f"pass{i}") for i in range(1, 11)]
        self.other_profiles = [Profile.objects.create(user=user) for user in self.other_users]
        self.actions = [
            Action.objects.create(user=user, verb="liked", target=self.other_users[i])
            for i, user in enumerate(self.other_users)
        ]
        # Make the user follow some other users for testing
        self.user.following.add(*self.other_users[:5])

    def test_liked_roses_success(self):
        # Log in as the test user
        self.client.login(username="Sam", password="testpass123")
        # Request to see the liked roses without page number
        response = self.client.get(reverse("roses_liked"))
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response template is "account/user/roses_liked.html"
        self.assertTemplateUsed(response, "account/user/roses_liked.html")
        # Assert that the response context contains the correct data
        self.assertEqual(response.context["section"], "roses_liked")
        self.assertEqual(response.context["page"], None)


    def test_liked_roses_pagination(self):
        # Log in as the test user
        self.client.login(username="Sam", password="testpass123")
        # Request to see the second page of the liked roses
        response = self.client.get(reverse("roses_liked"), {"page": "2"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response context contains the correct data
        self.assertEqual(response.context["page"], "2")
        self.assertEqual(str(response.context["roses"]), str(self.paginator.page(2)))

    def test_liked_roses_invalid_page(self):
        # Log in as the test user
        self.client.login(username="Sam", password="testpass123")
        # Request to see the liked roses without page number
        response = self.client.get(reverse("roses_liked"), {"page": "abc"})
        # Assert that the response status code is 200  - redirected to previous page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], "abc")
        self.assertEqual(str(response.context["roses"]), str(self.paginator.page(1)))

    def test_liked_roses_out_of_range_page(self):
        # Log in as the test user
        self.client.login(username="Sam", password="testpass123")
        # Request to see an out-of-range page of the liked roses
        response = self.client.get(reverse("roses_liked"), {"page": "-1"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], "-1")
        # Assert that the response contains the correct data
        self.assertEqual(str(response.context["roses"]), str(self.paginator.page(3)))

    def test_liked_roses_login_required(self):
        # Log out the test user
        self.client.logout()
        # Request to see the liked roses
        response = self.client.get(reverse("roses_liked"))
        # Assert that the response status code is 302
        self.assertEqual(response.status_code, 302)
        # Assert that the response redirects to the login page
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('roses_liked')}")


class UserRosesPhotoUploadedTest(TestCase):
    def setUp(self):
        # Create a user and a profile for testing
        self.user = User.objects.create_user(username="Sue", password="testpass123")
        self.profile = Profile.objects.create(user=self.user)
        # Create some roses data for testing
        rose = create_rose_objects(1, self.user)
        self.rose = Rose.objects.get(id=rose[0].id)
        # print(self.rose, rose[0])
        self.rose_photos = create_rose_pic_objects(55, self.rose, self.user)
        self.posted_pictures = RosePhoto.objects.filter(
                translations__language_code="en", picture_author=self.user
            ).all()
        self.paginator = Paginator(self.posted_pictures, 20)
        # Create some other users and actions for testing
        self.other_users = [User.objects.create_user(username=f"user{i}", password=f"pass{i}") for i in range(1, 11)]
        self.other_profiles = [Profile.objects.create(user=user) for user in self.other_users]
        self.actions = [
            Action.objects.create(user=user, verb="liked", target=self.other_users[i])
            for i, user in enumerate(self.other_users)
        ]
        # Make the user follow some other users for testing
        self.user.following.add(*self.other_users[:5])

    def test_photos_posted_basic(self):
        # Log in as the test user
        self.client.login(username="Sue", password="testpass123")
        # Request to see the posted photos without page number
        response = self.client.get(reverse("photos_posted"))
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response template is "account/user/photos_posted.html"
        self.assertTemplateUsed(response, "account/user/photos_posted.html")
        # Assert that the response context contains the correct data
        self.assertEqual(response.context["section"], "photos")
        self.assertEqual(response.context["page"], None)

    def test_rose_photos_pagination(self):
        # Log in as the test user
        self.client.login(username="Sue", password="testpass123")
        # Request to see the second page of the posted rose photos
        response = self.client.get(reverse("photos_posted"), {"page": "2"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response context contains the correct data
        self.assertEqual(response.context["page"], "2")

    def test_liked_rose_photos_out_of_range_page(self):
        # Log in as the test user
        self.client.login(username="Sue", password="testpass123")
        # Request to see an out-of-range page of the photos posted
        response = self.client.get(reverse("photos_posted"), {"page": "-1"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the correct data
        self.assertEqual(response.context["page"], "-1")
        # Assert that the response contains the last page data
        self.assertEqual(str(response.context["photos"]), str(self.paginator.page(3)))

    def test_posted_rose_photos_login_required(self):
        # Log out the test user
        self.client.logout()
        # Request to see the liked roses
        response = self.client.get(reverse("photos_posted"))
        # Assert that the response status code is 302
        self.assertEqual(response.status_code, 302)
        # Assert that the response redirects to the login page
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('photos_posted')}")


class UserArticlesPostedTest(TestCase):
    def setUp(self):
        # Create a user and a profile for testing
        self.user = User.objects.create_user(username="Mathue", password="testpass123")
        self.profile = Profile.objects.create(user=self.user)
        # Create some article data for testing 
        plant = create_plant_data(1, self.user)[0]
        issue = create_issue_type_data(1, self.user, plant)[0]
        article_category=create_article_category_data(1, self.user)[0]
        articles = create_article_data(42, self.user, issue, article_category)
        self.articles = Article.objects.filter(
                translations__language_code="en", author=self.user
            ).order_by('-created')
        # # print(self.rose, rose[0])
        self.paginator = Paginator(self.articles, 20)
        # Create some other users and actions for testing
        self.other_users = [User.objects.create_user(username=f"user{i}", password=f"pass{i}") for i in range(1, 11)]
        self.other_profiles = [Profile.objects.create(user=user) for user in self.other_users]
        self.actions = [
            Action.objects.create(user=user, verb="liked", target=self.other_users[i])
            for i, user in enumerate(self.other_users)
        ]
        # Make the user follow some other users for testing
        self.user.following.add(*self.other_users[:5])

    def test_article_posted_basic_view(self):
        # Log in as the test user
        self.client.login(username="Mathue", password="testpass123")
        # Request to see the posted photos without page number
        response = self.client.get(reverse("articles_posted"))
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response template is "account/user/articles_posted.html"
        self.assertTemplateUsed(response, "account/user/articles_posted.html")
        # Assert that the response context contains the correct data
        self.assertEqual(response.context["section"], "articles")
        self.assertEqual(response.context["page"], None)

    def test_rose_articles_pagination(self):
        # Log in as the test user
        self.client.login(username="Mathue", password="testpass123")
        # Request to see the second page of the posted articles
        response = self.client.get(reverse("articles_posted"), {"page": "2"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response context contains the correct data
        self.assertEqual(response.context["page"], "2")

    def test_articles_out_of_range_page(self):
        # Log in as the test user
        self.client.login(username="Mathue", password="testpass123")
        # Request to see an out-of-range page of the articless posted
        response = self.client.get(reverse("articles_posted"), {"page": "-10"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the correct data
        self.assertEqual(response.context["page"], "-10")
        # Assert that the response contains the last page data
        self.assertEqual(str(response.context["articles"]), str(self.paginator.page(3)))

    def test_posted_articles_login_required(self):
        # Log out the test user
        self.client.logout()
        # Request to see the liked roses
        response = self.client.get(reverse("articles_posted"))
        # Assert that the response status code is 302
        self.assertEqual(response.status_code, 302)
        # Assert that the response redirects to the login page
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('articles_posted')}")


class UserYouTubeVideosPostedTest(TestCase):
    def setUp(self):
        # Create a user and a profile for testing
        self.user = User.objects.create_user(username="Mathue", password="testpass123")
        self.profile = Profile.objects.create(user=self.user)
        # Create some rose data for testing 
        rose = create_rose_objects(1, self.user)[0]
        rose_obj = Rose.objects.get(id=rose.id)
        create_rose_video_objects(45, self.user, rose_obj)
        self.videos = RoseYoutubeVideo.objects.filter(video_author=self.user).order_by('-created')
        self.paginator = Paginator(self.videos, 20)
        # Create some other users and actions for testing
        self.other_users = [User.objects.create_user(username=f"user{i}", password=f"pass{i}") for i in range(1, 11)]
        self.other_profiles = [Profile.objects.create(user=user) for user in self.other_users]
        self.actions = [
            Action.objects.create(user=user, verb="liked", target=self.other_users[i])
            for i, user in enumerate(self.other_users)
        ]
        # Make the user follow some other users for testing
        self.user.following.add(*self.other_users[:5])

    def test_videos_posted_basic_view(self):
        # Log in as the test user
        self.client.login(username="Mathue", password="testpass123")
        # Request to see the posted videos without page number
        response = self.client.get(reverse("user_videos"))
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response template is "account/user/user_videos.html"
        self.assertTemplateUsed(response, "account/user/user_videos.html")
        # Assert that the response context contains the correct data
        self.assertEqual(response.context["section"], "videos")
        self.assertEqual(response.context["page"], None)

    def test_posted_videos_pagination(self):
        # Log in as the test user
        self.client.login(username="Mathue", password="testpass123")
        # Request to see the second page of the posted videos
        response = self.client.get(reverse("user_videos"), {"page": "2"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response context contains the correct data
        self.assertEqual(response.context["page"], "2")

    def test_posted_videos_range_page(self):
        # Log in as the test user
        self.client.login(username="Mathue", password="testpass123")
        # Request to see an out-of-range page of the videos posted
        response = self.client.get(reverse("user_videos"), {"page": "-10"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the correct data
        self.assertEqual(response.context["page"], "-10")
        # Assert that the response contains the last page data
        self.assertEqual(str(response.context["videos"]), str(self.paginator.page(3)))

    def test_posted_videos_login_required(self):
        # Log out the test user
        self.client.logout()
        # Request to see the posted videos
        response = self.client.get(reverse("user_videos"))
        # Assert that the response status code is 302
        self.assertEqual(response.status_code, 302)
        # Assert that the response redirects to the login page
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('user_videos')}")
