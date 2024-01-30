from unidecode import unidecode
from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.urls import reverse
from unittest.mock import patch

# from account.forms import UserRegistrationForm
from library.models import Plant, Issue, ArticleCategory, Article, Contact
from library.tests.test_views import create_plant_data, create_issue_type_data,\
    create_article_category_data, create_article_data, create_main_article_photo

# Rose model tests


class PlantModelTest(TestCase):
    def create_rose(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        plant = Plant.objects.create(
            genus="Aster",
            tribe="Astereae",
            author=self.user,
            scientific_name="Aster alpinus",
        )
        return plant

    def test_plant_creation(self):
        plant = self.create_rose()
        self.assertTrue(isinstance(plant, Plant))
        self.assertEqual(plant.__str__(), plant.genus)


class IssueModelTest(TestCase):
    def create_disease(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        self.plant = Plant.objects.create(
            genus="Aster",
            tribe="Astereae",
            author=self.user,
            scientific_name="Aster alpinus",
        )
        disease = Issue.objects.create(
            common_name="Mildew",
            main_causes="Damp weather and growing conditions",
            main_symptoms="Conspicuous mass of white threadlike hyphae and fruiting structures",
            caused_by="Erysiphales",
            timing="from early spring to frosts",
            area_affected="Leaves",
            author=self.user,
            scientific_name="Cladosporium",
            plants_affected=self.plant,
            beneficial=False,
        )
        return disease

    def test_disease_creation(self):
        disease = self.create_disease()
        self.assertTrue(isinstance(disease, Issue))
        self.assertEqual(disease.__str__(), disease.common_name)


class TestArticleCategoryModel(TestCase):
    def create_article_category(self):
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )

        category = ArticleCategory.objects.create(
            category_name="Diseases", description="Bad, bad category", author=self.user
        )
        return category

    def test_category_creation(self):
        category = self.create_article_category()
        self.assertTrue(isinstance(category, ArticleCategory))
        self.assertEqual(category.__str__(), category.category_name)
        self.assertEqual(category.category_name, "Diseases")
        self.assertEqual(category.description, "Bad, bad category")
        self.assertEqual(category.author.username, "Jill")

    def test_article_category_updated_filed(self):
        with patch.object(
            timezone, "now", return_value=timezone.now()
        ) as mock_now:
            category = self.create_article_category()
            category.save()
            self.assertEquals(category.category_name, "Diseases")
            self.assertEquals(category.description, "Bad, bad category")
            self.assertEquals(category.author.username, "Jill")
            self.assertEquals(
                category.category_slug, slugify(unidecode(category.category_name))
            )
            self.assertEquals(category.updated, timezone.now())


class TestArticleModel(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        self.plant = Plant.objects.create(
            genus="Aster",
            tribe="Astereae",
            author=self.user,
            scientific_name="Aster alpinus",
        )
        self.category = ArticleCategory.objects.create(
            category_name="Diseases",
            description="Bad, bad category",
            category_slug="diseases",
            author=self.user,
        )
        self.issue = Issue.objects.create(
            common_name="Mildew",
            main_causes="Damp weather and growing conditions",
            main_symptoms="Conspicuous mass of white threadlike hyphae and fruiting structures",
            caused_by="Erysiphales",
            timing="from early spring to frosts",
            area_affected="Leaves",
            author=self.user,
            scientific_name="Cladosporium",
            plants_affected=self.plant,
            beneficial=False,
        )
        self.article = Article.objects.create(
            title="New title",
            title_description="Title with another words",
            short_description="This explains a lot",
            body_1="Intro thoughts",
            body_2="Priblem description",
            body_3="What to do about it",
            body_4="Aother thoughts",
            summary="That's all falks!",
            author=self.user,
            category=self.category,
            issue_id=self.issue,
        )
        self.main_photo =  create_main_article_photo(self.article, self.issue)


    def test_article_creation(self):
        self.assertTrue(isinstance(self.article, Article))
        self.assertEqual(self.article.__str__(), self.article.title)
        self.assertEqual(self.article.title, "New title")
        self.assertEqual(self.article.summary, "That's all falks!")
        self.assertEqual(self.article.author.email, "jill@example.com")
     
        # test the get_main_photo method of the Article model
        self.assertEqual(self.article.get_main_photo(), self.main_photo) # the main photo of article1 should be photo1

    def test_article_slug(self):
        self.assertTrue(isinstance(self.article, Article))
        self.assertEqual(self.article.__str__(), self.article.title)
        # test article URL and get_absolute_url() method
        url = self.article.get_absolute_url()
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_article_updated_filed(self):
        with patch.object(
            timezone, "now", return_value=timezone.now()
        ) as mock_now:
            article = self.article
            article.save()
            self.assertEquals(article.title, "New title")
            self.assertEquals(article.body_2, "Priblem description")
            self.assertEquals(article.author.username, "Jill")
            self.assertEquals(article.issue_id.common_name, "Mildew")
            self.assertEquals(article.slug, slugify(unidecode(article.title)))
            self.assertEquals(article.updated, timezone.now())


class TestArticlePhoto(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        plant = create_plant_data(1, self.user)[0]
        issue = create_issue_type_data(1, self.user, plant)[0]
        issue_obj = Issue.objects.get(id=issue.id)
        article_category=create_article_category_data(1, self.user)[0]
        article_category_obj = ArticleCategory.objects.get(id=article_category.id)
        article = create_article_data(1, self.user, issue, article_category_obj)[0]
        self.article = Article.objects.get(id=article.id)
        self.photo = create_main_article_photo(self.article, issue)

    def test_photo_creatin(self):
        self.assertEqual(self.photo.__str__(), f"Photo {self.photo.id} for Article '{self.article}'")


class ContactModelTest(TestCase):
    def create_contact_data(self):
        contact_data = Contact.objects.create(
            first_name="Miss",
            last_name="Fine",
            email="missfine@example.com",
            phone="",
            subject="I have noticed something",
            message="By this I would like to pay your attention to the facts.",
            created=timezone.now(),
            replied=False,
        )
        return contact_data

    def test_contact_model(self):
        contact_info = self.create_contact_data()
        self.assertTrue(isinstance(contact_info, Contact))
        self.assertEqual(contact_info.__str__(), contact_info.subject)
