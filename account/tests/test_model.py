from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

# from account.forms import UserRegistrationForm
from account.models import Profile, Contact


class ProfileModelTest(TestCase):
    def create_profile(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        profile = Profile.objects.create(
            user=self.user,
            date_of_birth="1978-05-26",
        )
        return profile

    def test_profile_creation(self):
        profile = self.create_profile()
        profile.save()
        profile_username = profile.user.username
        self.assertTrue(isinstance(profile, Profile))
        self.assertEqual(profile.__str__(), f"Profile for user {profile_username}")
        self.assertEqual(profile.date_of_birth, "1978-05-26")


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
