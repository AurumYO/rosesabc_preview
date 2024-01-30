from django.test import TestCase
from django.contrib.auth.models import User
from .models import Action
from .utils import create_action


class ActionModelTest(TestCase):
    def setUp(self):
        # create some users and actions for testing
        self.user1 = User.objects.create_user(username="Anna", password="testpass123")
        self.user2 = User.objects.create_user(username="Gimmy", password="testpass456")
        self.action1 = Action.objects.create(user=self.user1, verb="following", target=self.user2)


    def test_action_string_representation(self):
        # test the __str__ method of the Action model
        self.assertEqual(str(self.action1), "Anna following Gimmy")
        self.assertEqual(self.action1.__str__(), "Anna following Gimmy")

    def test_action_ordering(self):
        # test the ordering of the Action model
        actions = Action.objects.all()
        self.assertEqual(actions[0], self.action1) # the most recent action should be first


class CreateActionTest(TestCase):
    def setUp(self):
        # create some users for testing
        self.user1 = User.objects.create_user(username="Anna", password="testpass123")
        self.user2 = User.objects.create_user(username="Gimmy", password="Testpass456")

    def test_create_action(self):
        # test the create_action function
        # create an action with a target
        result = create_action(self.user1, "following", self.user2)
        self.assertTrue(result) # the function should return True
        self.assertEqual(Action.objects.count(), 1) # the action should be saved in the database
        action = Action.objects.first()
        self.assertEqual(action.user, self.user1) # the action user should be user1
        self.assertEqual(action.verb, "following") # the action verb should be "followed"
        self.assertEqual(action.target, self.user2) # the action target should be user2
        # create an action without a target
        result = create_action(self.user2, "posted")
        self.assertTrue(result) # the function should return True
        self.assertEqual(Action.objects.count(), 2) # the action should be saved in the database
        action = Action.objects.first()
        self.assertEqual(action.user, self.user2) # the action user should be user2
        self.assertEqual(action.verb, "posted") # the action verb should be "posted"
        self.assertIsNone(action.target) # the action target should be None
        # create a similar action within a minute
        result = create_action(self.user2, "posted")
        self.assertFalse(result) # the function should return False
        self.assertEqual(Action.objects.count(), 2) # the action should not be saved in the database
        
