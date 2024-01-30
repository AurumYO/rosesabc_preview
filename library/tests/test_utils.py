import os
from django.conf import settings
from django.test import TestCase
from PIL import Image
from io import BytesIO
from django.core.files import File

from library.utils import resize_article_photo


class ResizeArticlePhotoTest(TestCase):
    # Test resize the image functionality for the main picture
    def test_resize_article_photo(self):
        # Create a sample image for testing
        sample_image = Image.new('RGB', (1500, 1000))

        # Create a BytesIO object to simulate file storage
        photo_buffer = BytesIO()
        sample_image.save(photo_buffer, 'JPEG')
        photo_buffer.seek(0)
        fake_file = File(photo_buffer, name='test.jpg')

        # Call the function with various cases and assert the results
        resized_image = resize_article_photo(fake_file, section_code=1)
        self.assertIsInstance(resized_image, File)
        # Add more assertions based on your expected behavior

        # Test with a small image
        small_image = Image.new('RGB', (800, 600))
        small_buffer = BytesIO()
        small_image.save(small_buffer, 'JPEG')
        small_buffer.seek(0)
        small_file = File(small_buffer, name='small_test.jpg')

        resized_small_image = resize_article_photo(small_file, section_code=0)
        self.assertIsInstance(resized_small_image, File)
        # Add more assertions based on your expected behavior

    