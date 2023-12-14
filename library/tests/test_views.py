from django.test import SimpleTestCase
from django.urls import reverse, resolve

from library.forms import ContactForm
from library.views import contact_us


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


class ContactUsPage(SimpleTestCase):
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
