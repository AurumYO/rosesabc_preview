import io
from uuid import uuid4
from unidecode import unidecode
from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import slugify

# from account.forms import UserRegistrationForm
from roses.models import (
    Rose,
    RoseAlternativeName,
    RosePhoto,
    RoseYoutubeVideo,
    RoseComment,
)

# Rose model tests


class RoseModelTest(TestCase):
    def setUp(self):
        # Set up a test user
        self.user = get_user_model().objects.create_user(
                    username="Jill", email="jill@example.com", password="testpass123"
                )
        # set Up additional Users for likes testing
        self.user2 = get_user_model().objects.create_user(
                    username="Kenneth", email="kenneth@example.com", password="testpass123"
                )
        self.user3 = get_user_model().objects.create_user(
                    username="Keira", email="keira@example.com", password="testpass123"
                )
        self.rose = Rose.objects.create(
            name="Patio Orange",
            colour="Orange",
            color_category="Orangewith red reverse",
            description="Very nice and bright",
            breeder="Peter Pancake",
            breeder_company="Paterate SA",
            aroma="Strong, Old rose",
            rose_series="Patiossa",
            parentage="Mme Cochette & Comandant Cecile Brunet",
            name_origin="Novel by Thomas Hardy",
            awards="ADR in 1998",
            rose_class="Modern Shrubs",
            rose_subclass="Patio Climber",
            type="Medium Shrub",
            flowering="Repeat Flowering",
            flower_size="Medium",
            flower_type="Semi-double",
            flower_form="cupped",
            flower_born="mostly solitary",
            growth_type="upright",
            height="from 100 cm to 150 cm",
            width="up to 100 cm tall",
            climate_zones="from USDA 5 to 10",
            foliage_colour="light-green",
            foliage_size="medium",
            foliage_surface="glossy",
            foliage_texture="reflexed",
            post_author=self.user,
            publish=False,
            created=timezone.now(),
            updated=timezone.now(),
            status="draft",
            aroma_strength=3,
            slug="mme-meilland-4fc949c81407",
            registration_code='3-35-40 (Meilland/"Peace")',
            registration_slug="mme-meilland-92a0a8321aa2",
            year_introduction="1935",
            health_rating=3,
            mixed_border=True,
            shade=True,
            cutting=False,
            containers=False,
            border=True,
            hedges=False,
            pergola=False,
            attracting_bees=False,
            landscaping=False,
            rock_gardens=False,
            large_structures=False,
            prunning=2,
            soil_types=7,
            sun_exposure=3,
            blackspots=2,
            mildew=2,
            botrytis=3,
            rust=3,
            cold_hardy=7,
            heat_resistance=3,
        )
        # Add users2 to the list of user's who liked the rose
        self.rose.users_like.add(self.user2)
        # create Rose objet without direct input or slug
        self.rose_without_slug = Rose.objects.create(
            name="Patio Orange",
            colour="Orange",
            color_category="Orangewith red reverse",
            description="Very nice and bright",
            breeder="Peter Pancake",
            breeder_company="Paterate SA",
            aroma="Strong, Old rose",
            rose_series="Patiossa",
            parentage="Mme Cochette & Comandant Cecile Brunet",
            name_origin="Novel by Thomas Hardy",
            awards="ADR in 1998",
            rose_class="Modern Shrubs",
            rose_subclass="Patio Climber",
            type="Medium Shrub",
            flowering="Repeat Flowering",
            flower_size="Medium",
            flower_type="Semi-double",
            flower_form="cupped",
            flower_born="mostly solitary",
            growth_type="upright",
            height="from 100 cm to 150 cm",
            width="up to 100 cm tall",
            climate_zones="from USDA 5 to 10",
            foliage_colour="light-green",
            foliage_size="medium",
            foliage_surface="glossy",
            foliage_texture="reflexed",
            post_author=self.user,
            publish=False,
            created=timezone.now(),
            updated=timezone.now(),
            status="draft",
            aroma_strength=3,
            registration_code='3-35-40 (Meilland/"Peace")',
            year_introduction="1935",
            health_rating=3,
            mixed_border=True,
            shade=True,
            cutting=False,
            containers=False,
            border=True,
            hedges=False,
            pergola=False,
            attracting_bees=False,
            landscaping=False,
            rock_gardens=False,
            large_structures=False,
            prunning=1,
            soil_types=7,
            sun_exposure=3,
            blackspots=2,
            mildew=2,
            botrytis=3,
            rust=3,
            cold_hardy=7,
            heat_resistance=3,
        )

    def test_rose_creation(self):
        self.assertTrue(isinstance(self.rose, Rose))
        self.assertEqual(self.rose.__str__(), "Patio Orange")
        self.assertEqual(str(self.rose), "Patio Orange")
        self.assertEqual(self.rose.slug, "mme-meilland-4fc949c81407")
        self.assertEqual(self.rose.registration_slug, "mme-meilland-92a0a8321aa2")
        self.assertEqual(self.rose.publish, False)

    def test_rose_url(self):
        url = self.rose.get_absolute_url()
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_rose_status_change(self):
        self.assertEqual(self.rose.publish, False)
        self.rose.status = "published"
        self.rose.save()
        self.assertEqual(self.rose.publish, True)

    def test_rose_slug_field_creation(self):
        self.rose_without_slug
        self.assertEqual(self.rose_without_slug.name, "Patio Orange")

    def test_rose_get_likes(self):
        self.rose.users_like.add(self.user)
        users_liked = self.rose.get_users_like()
        self.assertIn(self.user, users_liked)

    def test_get_followed_users_likes(self):
        self.rose.users_like.add(self.user)
        random_likes = self.rose.get_followed_users_likes()
        self.assertIn(self.user2, random_likes)
        self.assertEqual(len(random_likes), 2)
        # Add more users, who liked the Rose object
        self.rose.users_like.add(self.user3)
        random_likes = self.rose.get_followed_users_likes()
        self.assertEqual(len(random_likes), 2)


class RoseAlternativeNameTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # create Rose object
        self.rose = Rose.objects.create(
            name="Patio Orange",
            colour="Orange",
            color_category="Orangewith red reverse",
            description="Very nice and bright",
            breeder="Peter Pancake",
            breeder_company="Paterate SA",
            aroma="Strong, Old rose",
            rose_series="Patiossa",
            parentage="Mme Cochette & Comandant Cecile Brunet",
            name_origin="Novel by Thomas Hardy",
            awards="ADR in 1998",
            rose_class="Modern Shrubs",
            rose_subclass="Patio Climber",
            type="Medium Shrub",
            flowering="Repeat Flowering",
            flower_size="Medium",
            flower_type="Semi-double",
            flower_form="cupped",
            flower_born="mostly solitary",
            growth_type="upright",
            height="from 100 cm to 150 cm",
            width="up to 100 cm tall",
            climate_zones="from USDA 5 to 10",
            foliage_colour="light-green",
            foliage_size="medium",
            foliage_surface="glossy",
            foliage_texture="reflexed",
            post_author=self.user,
            publish=False,
            created=timezone.now(),
            updated=timezone.now(),
            status="draft",
            aroma_strength=3,
            registration_code='3-35-40 (Meilland/"Peace")',
            year_introduction="1935",
            health_rating=3,
            mixed_border=True,
            shade=True,
            cutting=False,
            containers=False,
            border=True,
            hedges=False,
            pergola=False,
            attracting_bees=False,
            landscaping=False,
            rock_gardens=False,
            large_structures=False,
            prunning=1,
            soil_types=7,
            sun_exposure=3,
            blackspots=2,
            mildew=2,
            botrytis=3,
            rust=3,
            cold_hardy=7,
            heat_resistance=3,
        )
        # create Alternative Name object
        self.alternative_name = RoseAlternativeName.objects.create(
            rose_code=self.rose,
            name="Pretty Betty",
        )

    def test_alternative_name_creation(self):
        self.assertIsInstance(self.alternative_name, RoseAlternativeName)
        self.assertEqual(self.alternative_name.name, "Pretty Betty")
        self.assertNotEqual(self.alternative_name.name, "Ugly Betty")
        self.assertEqual(self.alternative_name.__str__(), "Pretty Betty")

    def test_alternative_name_rose_url(self):
        url = self.alternative_name.get_absolute_url()
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)

    def test_alternative_name_rose_main_picture(self):
        picture = self.alternative_name.get_main_picture()
        self.assertEqual(picture, None)
        
    def test_get_alternative_english_name_(self):
        altertative_name = self.alternative_name.get_english_name()
        self.assertEqual(altertative_name, "Pretty Betty")


class RosePhotoTest(TestCase):
    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(1500, 1500), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "new_image.png"
        file.seek(0)
        return file

    def setUp(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # create rose
        self.rose = Rose.objects.create(
            name="Patio Orange",
            colour="Orange",
            color_category="Orangewith red reverse",
            description="Very nice and bright",
            breeder="Peter Pancake",
            breeder_company="Paterate SA",
            aroma="Strong, Old rose",
            rose_series="Patiossa",
            parentage="Mme Cochette & Comandant Cecile Brunet",
            name_origin="Novel by Thomas Hardy",
            awards="ADR in 1998",
            rose_class="Modern Shrubs",
            rose_subclass="Patio Climber",
            type="Medium Shrub",
            flowering="Repeat Flowering",
            flower_size="Medium",
            flower_type="Semi-double",
            flower_form="cupped",
            flower_born="mostly solitary",
            growth_type="upright",
            height="from 100 cm to 150 cm",
            width="up to 100 cm tall",
            climate_zones="from USDA 5 to 10",
            foliage_colour="light-green",
            foliage_size="medium",
            foliage_surface="glossy",
            foliage_texture="reflexed",
            post_author=self.user,
            publish=False,
            created=timezone.now(),
            updated=timezone.now(),
            status="draft",
            aroma_strength=3,
            registration_code='3-35-40 (Meilland/"Peace")',
            year_introduction="1935",
            health_rating=3,
            mixed_border=True,
            shade=True,
            cutting=False,
            containers=False,
            border=True,
            hedges=False,
            pergola=False,
            attracting_bees=False,
            landscaping=False,
            rock_gardens=False,
            large_structures=False,
            prunning=1,
            soil_types=7,
            sun_exposure=3,
            blackspots=2,
            mildew=2,
            botrytis=3,
            rust=3,
            cold_hardy=7,
            heat_resistance=3,
        )
        self.photo = RosePhoto.objects.create(
            title="Photo of rose Patio Orange",
            alt_text="rose Patio Orange",
            rose_data=self.rose,
            picture_author=self.user,
            picture=self.generate_photo_file(),
        )

        self.photo2 = RosePhoto.objects.create(
            title="Photo of rose Patio Orange2",
            alt_text="rose Patio Orange2",
            rose_data=self.rose,
            picture_author=self.user,
            unique_id="0a7476cc-d6c1-40ba-8ae1-606518c3497f",
            slug=None,
            picture=self.generate_photo_file(),
        )

    def test_rose_photo_upload(self):
        self.assertIsInstance(self.photo, RosePhoto)
        self.assertEqual(self.photo.__str__(), "Photo of rose Patio Orange")
        url = self.photo.get_absolute_url()
        self.response = self.client.get(url)
        self.assertEqual(self.response.status_code, 200)
        self.photo.delete()

    def test_rose_get_pictures(self):
        self.assertIsInstance(self.photo, RosePhoto)
        rose_picture = self.photo.rose_data.get_pictures()[1]
        self.assertEqual(rose_picture.__str__(), self.photo.__str__())
        self.photo.delete()

    def test_rose_photo_update(self):
        old_photo = self.photo.picture
        new_photo = self.generate_photo_file()
        self.photo.picture = new_photo
        self.photo.save()
        self.assertNotEqual(old_photo, new_photo)
        self.photo.delete()

    def test_rose_photo_without_slug(self):
        self.assertEqual(self.photo2.__str__(), "Photo of rose Patio Orange2")


class RoseYoutubeVideoTest(TestCase):
    def create_video_object(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # create rose
        self.rose = Rose.objects.create(
            name="Patio Orange",
            colour="Orange",
            color_category="Orangewith red reverse",
            description="Very nice and bright",
            breeder="Peter Pancake",
            breeder_company="Paterate SA",
            aroma="Strong, Old rose",
            rose_series="Patiossa",
            parentage="Mme Cochette & Comandant Cecile Brunet",
            name_origin="Novel by Thomas Hardy",
            awards="ADR in 1998",
            rose_class="Modern Shrubs",
            rose_subclass="Patio Climber",
            type="Medium Shrub",
            flowering="Repeat Flowering",
            flower_size="Medium",
            flower_type="Semi-double",
            flower_form="cupped",
            flower_born="mostly solitary",
            growth_type="upright",
            height="from 100 cm to 150 cm",
            width="up to 100 cm tall",
            climate_zones="from USDA 5 to 10",
            foliage_colour="light-green",
            foliage_size="medium",
            foliage_surface="glossy",
            foliage_texture="reflexed",
            post_author=self.user,
            publish=False,
            created=timezone.now(),
            updated=timezone.now(),
            status="draft",
            aroma_strength=3,
            registration_code='3-35-40 (Meilland/"Peace")',
            year_introduction="1935",
            health_rating=3,
            mixed_border=True,
            shade=True,
            cutting=False,
            containers=False,
            border=True,
            hedges=False,
            pergola=False,
            attracting_bees=False,
            landscaping=False,
            rock_gardens=False,
            large_structures=False,
            prunning=1,
            soil_types=7,
            sun_exposure=3,
            blackspots=2,
            mildew=2,
            botrytis=3,
            rust=3,
            cold_hardy=7,
            heat_resistance=3,
        )
        # create video object
        video = RoseYoutubeVideo.objects.create(
            rose_id=self.rose,
            video_author=self.user,
            link="https://www.youtube.com/watch?v=-ZJKdaEadt0",
            title="test video",
            active=True,
        )
        return video

    def test_video_model(self):
        new_video = self.create_video_object()
        new_video.save()
        self.assertIsInstance(new_video, RoseYoutubeVideo)
        self.assertEqual(new_video.__str__(), "test video")


class RoseCommentTest(TestCase):
    def create_comment(self):
        # create test user
        self.user = get_user_model().objects.create_user(
            username="Jill", email="jill@example.com", password="testpass123"
        )
        # create rose
        self.rose = Rose.objects.create(
            name="Patio Orange",
            colour="Orange",
            color_category="Orangewith red reverse",
            description="Very nice and bright",
            breeder="Peter Pancake",
            breeder_company="Paterate SA",
            aroma="Strong, Old rose",
            rose_series="Patiossa",
            parentage="Mme Cochette & Comandant Cecile Brunet",
            name_origin="Novel by Thomas Hardy",
            awards="ADR in 1998",
            rose_class="Modern Shrubs",
            rose_subclass="Patio Climber",
            type="Medium Shrub",
            flowering="Repeat Flowering",
            flower_size="Medium",
            flower_type="Semi-double",
            flower_form="cupped",
            flower_born="mostly solitary",
            growth_type="upright",
            height="from 100 cm to 150 cm",
            width="up to 100 cm tall",
            climate_zones="from USDA 5 to 10",
            foliage_colour="light-green",
            foliage_size="medium",
            foliage_surface="glossy",
            foliage_texture="reflexed",
            post_author=self.user,
            publish=False,
            created=timezone.now(),
            updated=timezone.now(),
            status="draft",
            aroma_strength=3,
            registration_code='3-35-40 (Meilland/"Peace")',
            year_introduction="1935",
            health_rating=3,
            mixed_border=True,
            shade=True,
            cutting=False,
            containers=False,
            border=True,
            hedges=False,
            pergola=False,
            attracting_bees=False,
            landscaping=False,
            rock_gardens=False,
            large_structures=False,
            prunning=1,
            soil_types=7,
            sun_exposure=3,
            blackspots=2,
            mildew=2,
            botrytis=3,
            rust=3,
            cold_hardy=7,
            heat_resistance=3,
        )
        # create comment object
        comment = RoseComment.objects.create(
            rose_post=self.rose,
            comment_author=self.user,
            body="Some new comment by user",
        )
        return comment

    def test_comment(self):
        new_comment = self.create_comment()
        new_comment.save()
        self.assertIsInstance(new_comment, RoseComment)
        self.assertTrue(
            str(new_comment),
            f"Comment by {new_comment.comment_author} on {new_comment.rose_post}",
        )
