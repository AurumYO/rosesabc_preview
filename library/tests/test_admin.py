from django.test import TestCase, Client
from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from library.tests.test_views import create_article_category_data,\
     create_plant_data, create_issue_type_data, create_article_data
from library.models import ArticleCategory, Article
from library.admin import ArticleCategoryAdmin
from library.admin import Article as AdminArticle


class AdminArticleCategoryTestCase(TestCase):
    def setUp(self):
        # Create a superuser for admin login
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin_password',
            email='admin@example.com'
        )
        # Create ArticleCategory for testing
        self.article_category = create_article_category_data(1, self.admin_user)[0]



    def test_get_prepopulated_fields(self):
        # Log in as the admin user
        self.client.login(username='admin', password='admin_password')

        # Instantiate your admin class
        admin_instance = ArticleCategoryAdmin(ArticleCategory, admin.site)

        # Call the get_prepopulated_fields method
        prepopulated_fields = admin_instance.get_prepopulated_fields(self.client, self.article_category)

        #Check if the returned value matches the expected value
        expected_prepopulated_fields = {"category_slug": ("category_name",)}
        self.assertEqual(prepopulated_fields, expected_prepopulated_fields)


class AdminArticleTestCase(TestCase):
    def setUp(self):
        # Create a superuser for admin login
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin_password',
            email='admin@example.com'
        )
        plant = create_plant_data(1, self.admin_user)[0]
        issue = create_issue_type_data(1, self.admin_user, plant)[0]
        # Create ArticleCategory for testing
        self.article_category = create_article_category_data(1, self.admin_user)[0]
        self.article = create_article_data(1, self.admin_user, issue, self.article_category)[0]

    def test_get_prepopulated_fields(self):
        # Log in as the admin user
        self.client.login(username='admin', password='admin_password')

        # Instantiate your admin class
        admin_instance = AdminArticle(Article, admin.site)

        # Call the get_prepopulated_fields method
        prepopulated_fields = admin_instance.get_prepopulated_fields(self.client, self.article)

        #Check if the returned value matches the expected value
        expected_prepopulated_fields = {"slug": ("title",)}
        self.assertEqual(prepopulated_fields, expected_prepopulated_fields)
