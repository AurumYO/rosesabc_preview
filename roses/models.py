import os
from uuid import uuid4
from unidecode import unidecode
from random import choice
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch.dispatcher import receiver
from taggit.managers import TaggableManager
from parler.models import TranslatableModel, TranslatedFields
from embed_video.fields import EmbedVideoField
from .utils import resize_photo


class Rose(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(_("Variety name"), max_length=150),
        colour=models.CharField(_("Colour"), max_length=150, blank=True),
        color_category=models.CharField(
            _("Colour Category"), max_length=50, blank=True
        ),
        description=models.TextField(_("Description"), blank=True),
        # other fields
    )

    post_author = models.ForeignKey(
        User, models.SET_NULL, blank=True, null=True, related_name="rose_posts"
    )
    publish = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, default="draft")
    # flower description
    aroma_strength = models.IntegerField(
        _("Aroma strength"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1,
        help_text=_(
            "Rate aroma from 1: 'No aroma', 2: 'Mild to none', 3: 'Mild', 4: 'Strong',  5: 'Very strong'"
        ),
    )
    # Other non-translatable fileds

    slug = models.SlugField(_("Slug"), max_length=150, blank=True, unique=True)
    
    sun_exposure = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        default=3,
        help_text="Sun exposure: 1 - 'shade', 2 - 'partial shade',\
                                                3 - 'full sun'",
    )

    

    # Interactions with users
    users_like = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="roses_liked", blank=True
    )
    total_user_likes = models.PositiveIntegerField(db_index=True, default=0)

    
    # Rose pictures
    class Meta:
        verbose_name = "rose"
        verbose_name_plural = "roses"

    def __str__(self):
        return self.name

    tags = TaggableManager()

    # custom same method that handels set the date of record edditing
    def save(self, *args, **kwargs):
        """On save, update timestamps, publish status, updates slug"""
        if self.id:
            self.updated = timezone.now()
        if self.status == "published":
            self.publish = True
        # make sures slugs is saved in correct form
        if not self.slug:
            self.slug = slugify(unidecode(self.name)) + "-" + str(uuid4()).split("-")[4]
        # make sures registration_slug is saved in correct form
        if not self.registration_slug:
            self.registration_slug = (
                slugify(unidecode(self.name)) + "-" + str(uuid4()).split("-")[4]
            )

        return super(Rose, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("roses:rose-detail", args=[self.slug])

    def get_comments(self):
        return self.comments.filter(parent=None).filter(active=True)

    def get_main_picture(self):
        rose_pic = RosePhoto.objects.filter(
            rose_data=self.id, main_picture=True
        ).first()
        return rose_pic if rose_pic else None

    def get_pictures(self):
        return self.rose_pics.filter(active=False)  # change later to = True

    def get_followed_users_likes(self):
        random_users_like = []
        user_ids = self.users_like.values_list("id", flat=True)
        # Get
        if len(user_ids) > 2:
            while len(random_users_like) < 2:
                random_id = choice(user_ids)
                random_user = self.users_like.get(id=random_id)
                if random_user not in random_users_like:
                    random_users_like.append(random_user)
        # if the current Rose post was liked by fewer than 2 users
        else:
            for u in user_ids:
                if u not in random_users_like:
                    user_liked = self.users_like.get(id=u)
                    random_users_like.append(user_liked)
        return random_users_like

    # return the list of users, who liked this particular rose.id
    def get_users_like(self):
        return self.users_like.all()

