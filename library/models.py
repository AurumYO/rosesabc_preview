from unidecode import unidecode
from uuid import uuid4
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from taggit.managers import TaggableManager
from parler.models import TranslatableModel, TranslatedFields
from .utils import resize_article_photo


# Articles category
class ArticleCategory(TranslatableModel):
    translations = TranslatedFields(
        category_name=models.CharField(_("Category"), max_length=50),
        description=models.CharField(_("Category description"), max_length=250),
    )
    category_slug = models.SlugField(
        _("Category_slug"), max_length=150, blank=True, unique=True
    )
    author = models.ForeignKey(
        User, models.SET_NULL, blank=True, null=True, related_name="category_author"
    )
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category_name

    # custom same method that handels set the date of record edditing
    def save(self, *args, **kwargs):
        """On save, update timestamps, create slug if not provided"""
        if self.id:
            self.updated = timezone.now()
        # make sures slugs is saved in correct form
        if not self.category_slug:
            self.category_slug = slugify(unidecode(self.category_name))
        return super(ArticleCategory, self).save(*args, **kwargs)


class Article(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=250),
        title_description=models.CharField(_("Title description"), max_length=250),
        short_description=models.TextField(_("Short description"), blank=True),
        body_1=models.TextField(_("Section 1"), blank=True),
        body_2=models.TextField(_("Section 2"), blank=True),
        body_3=models.TextField(_("Section 3"), blank=True),
        body_4=models.TextField(_("Section 4"), blank=True),
        summary=models.TextField(_("Summary"), blank=True),
    )
    # descriptive fields
    author = models.ForeignKey(
        User, models.SET_NULL, blank=True, null=True, related_name="article_author"
    )
    slug = models.SlugField(_("Slug"), max_length=50)
    category = models.ForeignKey(
        ArticleCategory,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="article_category",
    )
    issue_id = models.ForeignKey(
        Issue,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="article_issue",
    )
    publish = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    tags = TaggableManager()

    # custom same method that handels set the date of record edditing
    def save(self, *args, **kwargs):
        """On save, update timestamps, create slug if not provided"""
        if self.id:
            self.updated = timezone.now()
        # make sures slugs is saved in correct form
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        return super(Article, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("library:article-page", args=[self.slug])

    def get_main_photo(self):
        main_pic = ArticlePhotos.objects.filter(
            article=self.id, section_number=0
        ).first()
        return main_pic if main_pic else None
    
    