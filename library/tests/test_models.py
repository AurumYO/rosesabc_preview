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
            timezone, "now", return_value=datetime(2022, 12, 12, 11, 00)
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
    def create_article(self):
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
        article = Article.objects.create(
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
        return article

    def test_article_creation(self):
        article = self.create_article()
        self.assertTrue(isinstance(article, Article))
        self.assertEqual(article.__str__(), article.title)
        self.assertEqual(article.title, "New title")
        self.assertEqual(article.summary, "That's all falks!")
        self.assertEqual(article.author.email, "jill@example.com")

    def test_article_slug(self):
        article = self.create_article()
        self.assertTrue(isinstance(article, Article))
        self.assertEqual(article.__str__(), article.title)
        url = article.get_absolute_url()
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_article_updated_filed(self):
        with patch.object(
            timezone, "now", return_value=datetime(2023, 1, 1, 11, 00)
        ) as mock_now:
            article = self.create_article()
            article.save()
            self.assertEquals(article.title, "New title")
            self.assertEquals(article.body_2, "Priblem description")
            self.assertEquals(article.author.username, "Jill")
            self.assertEquals(article.issue_id.common_name, "Mildew")
            self.assertEquals(article.slug, slugify(unidecode(article.title)))
            self.assertEquals(article.updated, timezone.now())


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
