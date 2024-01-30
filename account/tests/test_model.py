import os
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse

# from account.forms import UserRegistrationForm
from account.models import Profile, Contact, Terms
from django.core.files.uploadedfile import SimpleUploadedFile


class ProfileModelTest(TestCase):
    def setUp(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            date_of_birth="1978-05-26",
            photo=SimpleUploadedFile(
                "test_photo.jpg",
                content=open("media/users/2023/09/25/IMG_20230616_071701.jpg", "rb").read(),
                content_type="image/jpeg",
            ),
            about_me="Test about me",
            region="Test region",
        )
        self.photo_file_path = self.profile.photo.path

    def test_profile_creation(self):
        self.assertTrue(isinstance(self.profile, Profile))
        self.assertEqual(self.profile.__str__(), f"Profile for user {self.profile.user.username }")
        self.assertEqual(self.profile.date_of_birth, "1978-05-26")

        
    def test_photo_deletion(self):
        # Assert that the photo file exists before deletion
        self.assertTrue(os.path.isfile(self.profile.photo.path))

        # Get the photo path after saving the profile
        photo_path = self.profile.photo.path

        # Delete the profile
        self.profile.delete()

        # Assert that the photo file is deleted after deletion
        self.assertFalse(os.path.exists(photo_path))


class ContactModelTest(TestCase):
    def create_user_follow_action(self):
        self.user1 = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        self.user2 = get_user_model().objects.create_user(
            username="Peter", email="peter@example.com", password="testpass123"
        )
        user_follow = Contact.objects.create(
            user_from=self.user1,
            user_to=self.user2,
        )
        return user_follow

    def test_user_following(self):
        follow_record = self.create_user_follow_action()
        follow_record.save()
        self.assertTrue(isinstance(follow_record, Contact))
        self.assertEqual(
            follow_record.__str__(),
            f"{follow_record.user_from} follows {follow_record.user_to}",
        )


class TestUserTerms(TestCase):
    def setUp(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            date_of_birth="1978-05-26",
            photo=SimpleUploadedFile(
                "test_photo.jpg",
                content=open("media/users/2023/09/25/IMG_20230616_071701.jpg", "rb").read(),
                content_type="image/jpeg",
            ),
            about_me="Test about me",
            region="Test region",
        )

        self.terms = Terms.objects.create(
            date_created=timezone.now(),
            date_updated=timezone.now(),
            date_user_agreed_on=timezone.now(),
            is_active=True,
            user_id=self.user,
        )

    def test_term_of_use(self):
        self.assertTrue(isinstance(self.terms, Terms))
        self.assertEqual(
            self.terms.__str__(),
            f"{self.user.username} agreed on terms on {self.terms.date_user_agreed_on}",
        )
        