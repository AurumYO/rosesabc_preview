import os
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.mail import BadHeaderError 
from django.test import SimpleTestCase, TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve

from library.forms import ContactForm
from library.views import contact_us

from faker import Faker
from unittest.mock import patch

from ..models import Plant, Issue, ArticleCategory, Article, ArticlePhotos


fake = Faker()


def create_plant_data(num_objects, plant_author):
    """
    Generates a list of fake Plant objects.
    
    Attributes:
        num_objects: The number of Plant objects to create.
        plant_author: The User object to assign as the author of each Plant object.
    Returns:
        list: A list of Plant objects with fake data.

    """
    plants = []
    for _ in range(num_objects):
        plant = Plant.objects.create(
            genus=fake.word(),
            author=plant_author,
            scientific_name=fake.word(),
            created=timezone.now(),
            updated=timezone.now(),
        )
        plants.append(plant)
    return plants

def create_issue_type_data(num_objects, issue_author, plant_obj):
    """
    Generates a list of fake Issue objects.
    
    Attributes:
        num_objects: The number of Issue objects to create.
        plant_author: The User object to assign as the author of each Issue object.
        plant_obj: The Plant object to assign as the plant affected by each Issue object.
    Returns:
        list: A list of Issue objects with fake data.

    """
    issues = []
    for _ in range(num_objects):
        issue = Issue.objects.create(
            common_name=fake.word(),
            main_causes=fake.sentence(),
            main_symptoms=fake.sentence(),
            caused_by=fake.sentence(),
            timing=fake.sentence(),
            area_affected=fake.sentence(),
            author=issue_author,
            plants_affected=plant_obj,
            scientific_name=fake.word(),
            beneficial=fake.boolean(),
            created=timezone.now(),
            updated=timezone.now(),
        )
        issues.append(issue)
    return issues

def create_article_category_data(num_objects, category_author):
    """
    Generates a list of fake Article Category objects.
    
    Attributes:
        num_objects: The number of Issue objects to create.
        category_author: The User object to assign as the author of each Article Category object.
    Returns:
        list: A list of Article Category objects with fake data.

    """
    article_categories = []
    for _ in range(num_objects):
        category = ArticleCategory.objects.create(
            category_name=fake.word(),
            description=fake.text(),
            category_slug=fake.slug(),
            author=category_author,
            created=timezone.now(),
            updated=timezone.now(),
        )
        article_categories.append(category)
    return article_categories

def create_article_data(num_objects, article_author, issue_obj, category_obj):
    """
    Generates a list of fake Article objects.
    
    Attributes:
        num_objects: The number of Article objects to create.
        article_author: The User object to assign as the author of each Article object.
        issue_obj: The Issue object to assign as the Article oobject.
        category_obj: The ArticleCatgory object to which the Article is assigned to
    Returns:
        list: A list of Article objects with fake data.

    """
    articles = []
    for _ in range(num_objects):
        article = Article.objects.create(
            title=fake.sentence(),
            title_description=fake.sentence(),
            short_description=fake.text(),
            body_1=fake.text(),
            body_2=fake.text(),
            body_3=fake.text(),
            body_4=fake.text(),
            body_5=fake.text(),
            body_6=fake.text(),
            body_7=fake.text(),
            author=article_author,
            slug=fake.slug(),
            category=category_obj,
            issue_id=issue_obj,
            publish=True,
            created=timezone.now(),
            updated=timezone.now(),
        )
        articles.append(article)
    return articles

article_picture_path = os.path.join(settings.BASE_DIR,\
                                    "media/articles/article_autumn-rose-pruning/autumn-rose-pruning.34c0841c8e98.jpg")
def create_main_article_photo(article_obj, issue_obj, pic_path=None):
    main_article_photo = ArticlePhotos.objects.create(
        article=article_obj,
        issue_id=issue_obj,
        photo=pic_path if pic_path else article_picture_path,
        title=fake.sentence(),
        alt_title=fake.sentence(),
        section_number=0,
        created=timezone.now(),
        updated=timezone.now(),
    )
    return main_article_photo


def create_article_photo(article_obj, issue_obj, section_num=None, pic_path=None):
    main_article_photo = ArticlePhotos.objects.create(
        article=article_obj,
        issue_id=issue_obj,
        photo=pic_path if pic_path else article_picture_path,
        title=fake.sentence(),
        alt_title=fake.sentence(),
        section_number=section_num if section_num else fake.random_int(min=1, max=7),
        created=timezone.now(),
        updated=timezone.now(),
    )
    return main_article_photo


class LibraryViewTest(TestCase):
    def setUp(self):
        # create a test client
        # self.client = Client()
        # create user for testing
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # create some articles for testing
        plant = create_plant_data(1, self.user)[0]
        issue = create_issue_type_data(1, self.user, plant)[0]
        article_category=create_article_category_data(1, self.user)[0]
        # create 30 fake Article objects for pagination
        create_article_data(30, self.user, issue, article_category)
        self.article1 = create_article_data(1, self.user, issue, article_category)[0]
        self.article2 = create_article_data(1, self.user, issue, article_category)[0]
        self.photo = create_main_article_photo(self.article1, issue)
        articles = Article.objects.filter(
                translations__language_code="en", author=self.user
            ).order_by('-created')
        self.paginator = Paginator(articles, 10)

        # set the language code for testing
        self.language_code = "en"

    def test_library_view_no_page_provided(self):
        # test the library view
        # # get the url of the view
        url = reverse("library:library")
        # make a GET request to the view
        response = self.client.get(url)
        # check the status code of the response
        self.assertEqual(response.status_code, 200)
        # check the template used by the view
        self.assertTemplateUsed(response, "library/library.html")
        # check the context data passed to the view
        self.assertIn("articles", response.context)
        self.assertIn("page", response.context)
        # check the pagination of the articles
        self.assertEqual(len(response.context["articles"]), 10) # the articles should be paginated by 10
        self.assertEqual(response.context["page"], None)# the default page should be None
        # check the language code of the articles
        self.assertEqual(response.context["articles"][0].language_code, self.language_code)

    def test_library_view_with_page_provided(self):
        # make a GET request to the view
        response = self.client.get(reverse("library:library"), {"page": "2"})
        # check the status code of the response
        self.assertEqual(response.status_code, 200)
        # check the template used by the view
        self.assertTemplateUsed(response, "library/library.html")
        # check the context data passed to the view
        self.assertIn("articles", response.context)
        self.assertIn("page", response.context)
        # check the pagination of the articles
        self.assertEqual(len(response.context["articles"]), 10) # the articles should be paginated by 10
        self.assertEqual(response.context["page"], "2")# the default page should be 2
        # check the language code of the articles
        self.assertEqual(response.context["articles"][0].language_code, self.language_code)

    def test_library_view_out_of_range_page(self):
        # Request to see an out-of-range page of the articless posted
        response = self.client.get(reverse("library:library"), {"page": "-10"})
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains the correct data
        self.assertEqual(response.context["page"], "-10")
        # Assert that the response contains the last page data
        self.assertEqual(len(response.context["articles"]), 2)


class CategoriesViewTest(TestCase):
    def setUp(self):
        # create user for testing
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # create some articles for testing
        plant = create_plant_data(1, self.user)[0]
        issue = create_issue_type_data(1, self.user, plant)[0]
        article_category = create_article_category_data(15, self.user)

    def test_categories_view(self):
        # make a GET request to the view
        response = self.client.get(reverse("library:categories"))


class CategoryViewTest(TestCase):
    def setUp(self):
        # create user for testing
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # set the language code
        self.language_code = "en"
        # create basic data for Category Articles object creation
        plant = create_plant_data(1, self.user)[0]
        issue = create_issue_type_data(1, self.user, plant)[0]
        # create 3 Article Categories
        self.article_category1 = create_article_category_data(1, self.user)[0]
        self.article_category1_slug = self.article_category1.category_slug
        self.article_category1_name = self.article_category1.category_name
        self.article_category2 = create_article_category_data(1, self.user)[0]
        self.article_category2_slug = self.article_category2.category_slug
        self.article_category3 = create_article_category_data(1, self.user)[0]
        self.article_category3_slug = self.article_category3.category_slug
        # create 16 Articles for first 2 Article Categories
        articles_cat1 = create_article_data(16, self.user, issue, self.article_category1)
        articles_cat1 = create_article_data(16, self.user, issue, self.article_category2)

    def test_category_articles_default_page(self):
        # make a GET request to the view
        response = self.client.get(reverse("library:category-page", args=[self.article_category1_slug]))
        # check the status code of the response
        self.assertEqual(response.status_code, 200)
        # check the template used by the view
        self.assertTemplateUsed(response, "library/category_page.html")
        # check the context data passed to the view
        self.assertIn("articles", response.context)
        self.assertIn("page", response.context)
        self.assertEqual(response.context["category_name"], self.article_category1_name)
        # check the pagination of the articles
        self.assertEqual(len(response.context["articles"]), 15) # the articles should be paginated by 15
        self.assertEqual(response.context["page"], None) # the default page should be 1
        # check the language code of the articles
        self.assertEqual(response.context["articles"][0].language_code, self.language_code)

    def test_category_articles_valid_page(self):
        response = self.client.get(reverse("library:category-page", args=[self.article_category1_slug]) + "?page=2")
        # check the status code of the response
        self.assertEqual(response.status_code, 200)
        # the articles should be paginated by 1
        self.assertEqual(len(response.context["articles"]), 1)
        self.assertEqual(response.context["page"], "2")

    def test_category_articles_nonvalid_page(self):
        response = self.client.get(reverse("library:category-page", args=[self.article_category1_slug]) + "?page=-100")
        # check the status code of the response
        self.assertEqual(response.status_code, 200)
        # the articles should be paginated by 1
        self.assertEqual(len(response.context["articles"]), 1)
        self.assertEqual(response.context["page"], "-100")

    def test_no_category_provided(self):
        response = self.client.get(reverse("library:category-page", args=[None]))
        # check the status code is 302 redirected
        self.assertEqual(response.status_code, 302)


class ArticlePageTest(TestCase):
    def setUp(self):
        # create user for testing
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # set the language code
        self.language_code = "en"
        # create basic data for Category Articles object creation
        plant = create_plant_data(1, self.user)[0]
        issue = create_issue_type_data(1, self.user, plant)[0]
        # create Article Category
        self.article_category = create_article_category_data(1, self.user)[0]
        # create Article object
        self.article = create_article_data(1, self.user, issue, self.article_category)[0]
        self.article_slug = self.article.slug
        # Create photos for the article
        main_pic = create_main_article_photo(self.article, issue)
        section_1_pic = create_article_photo(self.article, issue, 1)
        # Create Article Photo objects from large picture 
        self.article2= create_article_data(1, self.user, issue, self.article_category)[0]
        large_pic_path= os.path.join(settings.BASE_DIR,\
                                     "media/articles/article_autumn-rose-pruning/P1030498.JPG")
        main_pic2 = create_main_article_photo(self.article2, issue, pic_path=large_pic_path)


    def test_article_page_view(self):
        # make a GET request to the view
        response = self.client.get(reverse("library:article-page", args=[self.article.slug]))
        # check the status code of the response
        self.assertEqual(response.status_code, 200)
        # check the template used by the view
        self.assertTemplateUsed(response, "library/article_page.html")


class AboutPage(SimpleTestCase):
    def setUp(self):
        url = reverse("library:about")
        self.response = self.client.get(url)

    def test_about_page_english(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "About Roses ABC")
        self.assertNotContains(self.response, "БібліотекаТроянд")

    def test_about_page_tempalate_used(self):
        self.assertTemplateUsed(self.response, "about.html")


class GardensTest(TestCase):
    def setUp(self):
        url = reverse("library:gardens")
        self.response = self.client.get(url)

    def test_gardens_view_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "Gardens section is currently scheduled for development.")
        self.assertTemplateUsed(self.response, "library/gardens/gardens.html")


class ContactUsPage(TestCase):
    def setUp(self):
        url = reverse("library:contact-us")
        self.response = self.client.get(url)

    def test_about_page_english(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "Contact us")
        self.assertNotContains(self.response, "БібліотекаТроянд")

    def test_about_page_tempalate_used(self):
        self.assertTemplateUsed(self.response, "library/contact_us.html")

    def test_contact_us_url_resolves_contactusview(self):
        view = resolve("/en/library/contact-us")
        self.assertEqual(view.func.__name__, contact_us.__name__)

    def test_contact_us_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, ContactForm)
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_post_valid_form(self):
        # test the view with a valid form data
        # get the url of the view
        url = reverse("library:contact-us")
        # create a valid form data
        form_data = {
            "first_name": "Lucy",
            "last_name": "Lawless",
            "email": "lucy@example.com",
            "subject": "Test Subject",
            "phone": "3709787866",
            "message": "Test Message",
        }
        # mock the send_mail function
        with patch("library.views.send_mail") as mock_send_mail:
            # make a POST request to the view
            response = self.client.post(url, form_data)
            # check the status code of the response
            self.assertEqual(response.status_code, 200) # the response should be a 200 OK
            # check the template used by the response
            self.assertTemplateUsed(response, "roses/home.html") # the response should use the roses/home.html template
            # check the context data passed to the response
            self.assertIn("messages", response.context) # the response should have a messages object
            # check the mock send_mail function call
            mock_send_mail.assert_called_once_with(
                "Test Subject",
                "Test Message",
                "lucy@example.com",
                ["info.rosesabc@gmail.com"],
            ) # the mock send_mail function should be called once with the form data

    def test_post_invalid_form(self):
        # test the view with a invalid form data
        # get the url of the view
        url = reverse("library:contact-us")
        # create a valid form data
        form_data = {
            "first_name": "",
            "last_name": "Lawless",
            "email": "lucyexample.com",
            "subject": "Test Subject",
            "phone": "",
            "message": "",
        }
        # mock the send_mail function
        with patch("library.views.send_mail") as mock_send_mail:
            # make a POST request to the view
            response = self.client.post(url, form_data)
            # check the status code of the response
            self.assertEqual(response.status_code, 200) # the response should be a 200 OK
            # check the template used by the response
            self.assertTemplateUsed(response, "library/contact_us.html") # the response should use the library/contact_us.html template
            # check the context data passed to the response
            self.assertIn("form", response.context) # the response should have a form object
            self.assertFalse(response.context["form"].is_valid()) # the form should be invalid
            # check the mock send_mail function call
            mock_send_mail.assert_not_called() # the mock send_mail function should not be called


    def test_bad_header_error(self):
        # test the view with a bad header error
        # get the url of the view
        url = reverse("library:contact-us")
        # create a valid form data
        form_data = {
            "subject": "Test Subject",
            "email": "test@example.com",
            "message": "Test Message",
        }
        # mock the send_mail function to raise the BadHeaderError
        with patch("library.views.send_mail") as mock_send_mail:
            mock_send_mail.side_effect = BadHeaderError
            # make a POST request to the view
            response = self.client.post(url, form_data)
            # check the status code of the response
            self.assertEqual(response.status_code, 200) # the response should be a 200 OK
            # check the content of the response
            # self.assertIn("Invalid Header Found!", response.content.decode()) # the response should contain the error message


class TermsAndConditionsViewPageTest(TestCase):
    def setUp(self):
        url = reverse("library:terms-and-conditions")
        self.response = self.client.get(url)

    def test_terms_and_security_page_english(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "Terms and Conditions")
        self.assertNotContains(self.response, "Правила та Умови")

    def test_terms_and_security_page_tempalate_used(self):
        self.assertTemplateUsed(self.response, "terms_and_conditions.html")

    # def test_terms_and_security_page_ukrainian(self):
    #     url = reverse("library:terms-and-conditions")
    #     self.response = self.client.get(url)
    #     self.assertEqual(self.response.status_code, 200)
    #     self.assertContains(self.response, "Terms and Conditions")
    #     self.assertNotContains(self.response, "Правила та Умови")

class PrivacyAndSecurityViewPageTest(TestCase):
    def setUp(self):
        url = reverse("library:privacy-and-security")
        self.response = self.client.get(url)

    def test_privacy_and_security_page_view(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "Privacy and Security")
        self.assertNotContains(self.response, "Конфіденційність та Безпека")

    def test_privacy_and_security_page_tempalate_used(self):
        self.assertTemplateUsed(self.response, "privacy_and_security.html")


class AccessibilityViewPageTest(TestCase):
    def setUp(self):
        url = reverse("library:accessibility")
        self.response = self.client.get(url)

    def test_privacy_and_security_page_view(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "Assistance")
        self.assertNotContains(self.response, "Конфіденційність та Безпека")


class SitemapViewTest(TestCase):
    def setUp(self):
        url = reverse("library:sitemap")
        self.response = self.client.get(url)
    
    def test_sitemap_page_english(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "Sitemap")
        self.assertTemplateUsed(self.response, "sitemap.html")
    

