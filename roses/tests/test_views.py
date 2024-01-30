import os
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse, resolve
from taggit.managers import TaggableManager
from taggit.models import Tag
from faker import Faker

# from account.forms import UserRegistrationForm
from roses.models import Rose, RoseAlternativeName, RosePhoto, RoseYoutubeVideo, RoseComment
from roses.views import roses
from library.tests.test_views import create_plant_data, create_issue_type_data,\
      create_article_category_data, create_article_data


fake = Faker()


def create_rose_objects(num_objects, user_obj, tags_obj=None):
    """
    Template for creating fake Rose objects
    
    Attributes:
        unum_objects: takes interger values returns given nomber of Rose objects

    """
    roses = []
    tags = TaggableManager()
    for _ in range(num_objects):
        rose = Rose.objects.create(
            name=fake.word(),
            colour=fake.color_name(),
            color_category=fake.text(),
            description=fake.paragraph(),
            breeder=fake.name(),
            breeder_company=fake.company(),
            aroma=fake.sentence(),
            rose_series=fake.word(),
            parentage=fake.sentence(),
            name_origin=fake.word(),
            awards=fake.sentence(),
            rose_class=fake.word(),
            rose_subclass=fake.word(),
            type=fake.word(),
            flowering=fake.word(),
            flower_size=fake.word(),
            flower_type=fake.word(),
            flower_form=fake.word(),
            flower_born=fake.word(),
            growth_type=fake.word(),
            height=fake.random_int(min=50, max=200),
            width=fake.random_int(min=50, max=150),
            climate_zones=fake.random_int(min=1, max=11),
            foliage_colour=fake.word(),
            foliage_size=fake.word(),
            foliage_surface=fake.word(),
            foliage_texture=fake.word(),
            post_author=user_obj,
            publish=True,
            created=timezone.now(),
            updated=timezone.now(),
            status='published',
            aroma_strength=fake.random_int(min=1, max=5),
            slug=fake.slug(),
            registration_code=fake.word(),
            registration_slug=fake.slug(),
            year_introduction=fake.year(),
            health_rating=fake.random_int(min=1, max=5),
            mixed_border=fake.boolean(),
            shade=fake.boolean(),
            cutting=fake.boolean(),
            containers=fake.boolean(),
            border=fake.boolean(),
            hedges=fake.boolean(),
            pergola=fake.boolean(),
            attracting_bees=fake.boolean(),
            landscaping=fake.boolean(),
            rock_gardens=fake.boolean(),
            large_structures=fake.boolean(),
            prunning=fake.random_int(min=1, max=5),
            soil_types=fake.random_int(min=1, max=10),
            sun_exposure=fake.random_int(min=1, max=5),
            blackspots=fake.random_int(min=1, max=5),
            mildew=fake.random_int(min=1, max=5),
            botrytis=fake.random_int(min=1, max=5),
            rust=fake.random_int(min=1, max=5),
            cold_hardy=fake.random_int(min=1, max=10),
            heat_resistance=fake.random_int(min=1, max=5),
            tags = "hybrid" if not tags_obj else tags_obj,
        )
        rose.users_like.add(user_obj)
        roses.append(rose)
    return roses

def create_rose_alternative_name_objects(num_objects, rose_obj, name_obj=None):
    """
    Template for creating fake Rose objects
    
    Attributes:
        unum_objects: takes interger values returns given nomber of Rose objects

    """
    alt_names = []
    for _ in range(num_objects):
        alter_name = RoseAlternativeName.objects.create(
            rose_code=rose_obj,
            name=fake.word() if not name_obj else str(name_obj + fake.word()),
            slug=fake.slug(),
            created=timezone.now(),
            updated=timezone.now(),
        )
        alt_names.append(alter_name)
    return alt_names

picture_path = os.path.join(settings.BASE_DIR, "media/roses/rose_everepra/everepra.312d876085f5.jpg")

def create_rose_pic_objects(num_objects, rose_obj, author):
    """
    Template for creating fake RosePhoto objects
    
    Attributes:
        num_objects: takes interger values ret,urns given nomber of Rose objects
        rose_obj: odject from a Rose model
        author: author, User objec
    """
    photos = []
    for _ in range(num_objects):
        photo = RosePhoto.objects.create(
            title=fake.word(),
            alt_text=fake.text(),
            rose_data=rose_obj,
            picture_author=author,
            picture=picture_path,
            slug=fake.slug(),
            created=timezone.now(),
            updated=timezone.now(),
            active=True,
            main_picture=fake.boolean(),
            promo_pic=fake.boolean(),
        )
        photos.append(photo)
    return photo


def create_rose_video_objects(num_objects, author, rose_obj):
    videos = []
    for _ in range(num_objects):
        video = RoseYoutubeVideo.objects.create(
            rose_id=rose_obj,
            video_author=author,
            link='https://youtube.com/shorts/4scbFsw6dsQ?si=J4hMUZ06vWU8sg8O',
            title=fake.sentence(),  
            created=timezone.now(),
            modified=timezone.now(),
            active=True, 
        )
        videos.append(video)
    return videos


class TestHomePageView(TestCase):
    def setUp(self):
        # create test user for Rose objects creation 
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # create test Rose object
        self.roses = create_rose_objects(20, self.user)
         # create some articles for testing
        plant = create_plant_data(1, self.user)[0]
        issue = create_issue_type_data(1, self.user, plant)[0]
        article_category=create_article_category_data(1, self.user)[0]
        # create 30 fake Article objects for pagination
        create_article_data(4, self.user, issue, article_category)

    def text_home_page_view(self):
        # Test GET request to Home pahe
        response = self.client.get(reverse("home"))
        # check the status code of the response
        self.assertEqual(response.status_code, 200)
        # check the template used by the view
        self.assertTemplateUsed(response, "roses/home.html")
        # test if rose and Article objects are present in the context response
        self.assertIn("roses", response.context)
        self.assertIn("articles", response.context)
        # Check in the Home page displays the correct number of Rose and Article objects
        self.assertEqual(len(response.context["roses"]), 9)
        self.assertEqual(len(response.context["articles"]), 3)


class HomePageViewTest(TestCase):
    def setUp(self):
        url = reverse("roses:roses")
        self.response = self.client.get(url)
        
        
    def test_roses_general_page_view(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "We have all information about rose varieties in our encyclopedia")


class RoseListViewTest(TestCase):
    def setUp(self):
        # create test user for Rose objects creation 
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # Create roses with specific tag
        self.tag = Tag.objects.create(name='florists', slug='florists')
        self.tag2 = Tag.objects.create(name='hybrid', slug='hybrid')
        # create test Rose object
        self.roses = create_rose_objects(25, self.user, self.tag2)
        self.roses_tagged = create_rose_objects(14, self.user, self.tag.name)
        self.test_slug = get_object_or_404(Tag, slug=self.tag)
    
    def test_roses_list_page_view_without_tags_and_page(self):
        # Simulate Get request to List of Latest roses view
        response = self.client.get(reverse("roses:roses-list"))
        # Check the status code
        self.assertEqual(response.status_code, 200)
        # Check if the correct template was used
        self.assertTemplateUsed(response, "roses/post/roses_list.html")
        # Check the pagination of the Rose object
        self.assertEqual(response.context["page"], None)
        # Test if the number of Rose object is 12 per page
        self.assertEqual(len(response.context["roses"]), 12)

    def test_roses_list_page_view_without_page(self):
        # Simulate Get request to List of Latest roses view
        response = self.client.get(reverse("roses:roses-list") + "?page=2")
        # Check the status code
        self.assertEqual(response.status_code, 200)
        # Check if the correct template was used
        self.assertTemplateUsed(response, "roses/post/roses_list.html")
        # Check the pagination of the Rose object
        self.assertEqual(response.context["page"], "2")
        # Test if the number of Rose object is 12 per page
        self.assertEqual(len(response.context["roses"]), 12)


    def test_roses_list_page_view_with_tags_(self):
        # Simulate Get request to List of Latest roses view
        response = self.client.get(reverse("roses:roses-list-by-tag", args=["florists"]))
        # Check the status code
        self.assertEqual(response.status_code, 200)
        # Check if the correct template was used
        self.assertTemplateUsed(response, "roses/post/roses_list.html")
        # Check if the Rose object with correct tag "florists" are present on page
        # self.assertEqual(response.context["tag"].name, "florists")
        # # Test if the number of Rose object with tag "florists" is 10
        # self.assertEqual(len(response.context["roses"]), 12)

    def test_view_returns_paginated_roses(self):
        # Simulate Get request to List of Latest roses view with tag "florists" and page 2
        response = self.client.get(reverse("roses:roses-list-by-tag", kwargs={'tag_slug': "hybrid"}) + "?page=2")
        # Check if the correct template was used
        self.assertEqual(response.status_code, 200)
        # Check if the correct template was used
        self.assertTemplateUsed(response, "roses/post/roses_list.html")
        #Check if the Rose object with correct tag "florists" are present on page
        self.assertEqual(response.context["tag"].name, "hybrid")
        # print(response.context)
        # # Test if the number of Rose object with tag "florists" is 10
        # self.assertEqual(len(response.context["roses"]), 2)
        # # Check the current page number
        # self.assertEqual(response.context["page"], "2")

    def test_view_returns_last_page_if_page_is_out_of_range(self):
        # Test that the view returns the last page if the page is out of range
        response = self.client.get(reverse("roses:roses-list"), {"page": "100"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["roses"]), 3) # There are 3 roses on the last page
        self.assertEqual(response.context["page"], "100") # The page number displayed still 100
    

class SearchPageViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        # Test that the view exists at the expected URL
        response = self.client.get("/roses/search/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        # Test that the view is accessible by its name
        response = self.client.get(reverse("roses:roses-search"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        # Test that the view uses the correct template
        response = self.client.get(reverse("roses:roses-search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "roses/search/roses_search.html")


class RosesSearchResultsViewTest(TestCase):
    def setUp(self):
        # create test user for Rose objects creation 
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # Create some test data for roses and alternative names
        self.rose = create_rose_objects(1, self.user)[0]
        self.alternative_name = RoseAlternativeName.objects.create(
            rose_code=self.rose,
            name="Pretty Betty",
        )
        fake_name = "Pretty "
        self.alternative_names = create_rose_alternative_name_objects(45, self.rose, fake_name)

    def test_roses_search_results_with_query(self):
        # Use the Django test client to simulate a GET request
        client = Client()
        # Define the search query
        query = 'Pretty Betty'
        # Get the URL for the roses_search_results view with the query parameter
        url = reverse("roses:roses-search-results") + f"?q={query}"
        # Make a GET request with the specified query
        response = client.get(url)
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Add more assertions as needed to check the content of the response
        # For example, you can check if the query is present in the response content
        self.assertContains(response, query)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'roses/search/roses_search_results.html')

    def test_roses_search_results_with_empty_query(self):
        # Test behavior when the query is empty
        client = Client()
        url = reverse("roses:roses-search-results")
        response = client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_roses_search_results_valid_pagination(self):
        # Use the Django test client to simulate a GET request
        client = Client()
        # Define the search query
        query = "Pretty "
        # Get the URL for the roses_search_results view with the query parameter
        url = reverse("roses:roses-search-results") + f"?q={query}&page=2"
        response = client.get(url)
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # check if the quesry in correct
        self.assertEqual(response.context["query"], query)
         # The page number must be 2
        # self.assertEqual(response.context["page"], "2")
        self.assertEqual(len(response.context["roses"]), 20)

    def test_roses_search_results_invalid_pagination(self):
        # Use the Django test client to simulate a GET request
        client = Client()
        # Define the search query
        query = "Pretty"
        # Get the URL for the roses_search_results view with the query parameter
        url = reverse("roses:roses-search-results") + f"?q={query}&page=-20"
        response = client.get(url)
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
         # The page number must be -20
        self.assertEqual(response.context["page"], "-20")
        self.assertEqual(len(response.context["roses"]), 6)



class AlphabetListingView(TestCase):
    def setUp(self):
        # create test user for Rose objects creation 
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # Create some test data for roses and alternative names
        self.rose = create_rose_objects(25, self.user)[0]
        self.alternative_names = create_rose_alternative_name_objects(15, self.rose)

    def test_rose_alphabet_basic_english_view(self):
        # Use the Django test client to simulate a GET request
        client = Client()
        # Get the URL for the roses_search_results view with the query parameter and language code
        url = reverse('roses:roses-alphabet')
        # Define the LANGUAGE_CODE parameter to 'en'
        language_code = "en"
        response = client.get(url, HTTP_ACCEPT_LANGUAGE=f"{language_code}")
        # Check the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check if the correct template is used
        self.assertTemplateUsed(response, 'roses/search/roses_alphabet.html')     
        # Check if correct language is used in the template
        self.assertContains(response, "Roses alphabetically")
        # Check if correct language is used in the template
        self.assertNotContains(response, "Троянди за алфавітом")

    def test_rose_alphabet_basic_ukrainian_view(self):
        # Use the Django test client to simulate a GET request
        client = Client()
        # Get the URL for the roses_search_results view with the query parameter and language code
        url = reverse('roses:roses-alphabet', kwargs={'letter': "Ю"})
        # Define the LANGUAGE_CODE parameter to 'en'
        # with activate('uk'):
        #     response = client.get(url)
        # # Check the response status code is 200 (OK)
        # self.assertEqual(response.status_code, 200)
        # print(response.context)
        # # Check if the correct template is used
        # self.assertTemplateUsed(response, "roses/search/roses_alphabet.html")     
        # # Check if correct language is used in the template
        # self.assertContains(response, "Троянди за алфавітом")
        # # Check if correct language is used in the template
        # self.assertNotContains(response, "Roses alphabetically")


class RoseViewTests(TestCase):
    def setUp(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        self.tag = Tag.objects.create(name='florists', slug='florists')
        self.rose = create_rose_objects(1, self.user, self.tag.name)[0]
        self.alternative_names = create_rose_alternative_name_objects(15, self.rose)
        self.rose_slug = self.rose.slug

        # print("Rose slug", self.rose_slug)
        # create rose comment to test
        # comment = RoseComment.objects.create(
        #     rose_post=self.rose,
        #     comment_author=self.user,
        #     body="Some new comment",
        #     created="2023-01-29T11:39:19.534Z",
        #     updated="2023-01-20T11:39:19.534Z",
        # )
        # comment.save()

    def test_rose_detail_view_page(self):
        pass



class LandscapeIdeasViewTest(TestCase):
    def setUp(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        self.rose = create_rose_objects(57, self.user)

    def test_landscape_ideas_page(self):
        response = self.client.get(reverse("roses:landscape-ideas"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "roses/pages/landscape_ideas.html")
        self.assertContains(response, "Select your category")
        self.assertContains(response, "Select  category")


    # def test_lanscape_ideas_with_ideas_context(self):
    #     idea = "border"
    #     response = self.client.get(
    #         reverse("roses:landscape-ideas", kwargs={"idea": idea})
    #     )
    #     self.assertEqual(response.status_code, 200)
