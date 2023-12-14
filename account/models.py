from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """
    User Profile model for storing additional information about a user.

    Attributes:
        user (User): The user associated with this profile.
        date_of_birth (Date): The user's date of birth (optional).
        photo (Image): The user's profile photo (optional).
        about_me (str): A text field for additional information about the user (optional).
        region (str): The user's region or location (optional).

    Methods:
        __str__(): Returns a string representation of the profile.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to="users/%Y/%m/%d/", blank=True)
    about_me = models.TextField(_("About Me"), blank=True)
    region = models.CharField(_("Where You from?"), blank=True, max_length=255)

    def __str__(self):
        """
        Returns a string representation of the profile.

        Example:
            Profile for user john_doe
        """
        return f"Profile for user {self.user.username}"


@receiver(post_delete, sender=Profile)
def mymodel_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance:
        instance.photo.delete(False)


# Model which store th records on user agreement to the Terms
# and Conditions and on Privacy and Security
class Terms(models.Model):
    """
    Model to store user agreements to the Terms and Conditions.

    Attributes:
        date_created (DateTime): The timestamp when the agreement record was created.
        date_updated (DateTime): The timestamp when the agreement record was last updated.
        date_user_agreed_on (DateTime): The timestamp when the user agreed to the terms.
        is_active (bool): A boolean indicating whether the agreement is currently active.
        user_id (User): The user associated with this agreement record.

    Methods:
        __str__(): Returns a string representation of the user's agreement.
    """
        
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(default=timezone.now)
    date_user_agreed_on = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    user_id = models.ForeignKey(
        User, related_name="user_confirmed_agreement", on_delete=models.CASCADE
    )

    def __str__(self):
        """
        Returns a string representation of the user's agreement.

        Example:
            JohnDoe agreed on terms on 2023-01-01 12:34:56
        """
        return f"{self.user_id.username} agreed on terms on {self.date_user_agreed_on}"


# Followers model
class Contact(models.Model):
    """
    Model to store user relationships where one user follows another.

    Attributes:
        user_from (User): The user initiating the follow relationship.
        user_to (User): The user being followed.
        created (DateTime): The timestamp when the follow relationship was created.

    Meta:
        ordering (List): Specifies the default ordering for the model based on the 'created' attribute.

    Methods:
        __str__(): Returns a string representation of the follow relationship.
    """
    
    user_from = models.ForeignKey(
        "auth.User", related_name="rel_from_set", on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        "auth.User", related_name="rel_to_set", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        """
        Returns a string representation of the follow relationship.

        Example:
            JohnDoe follows JaneDoe
        """
        return f"{self.user_from} follows {self.user_to}"


# Add fields to User dynamically
user_model = get_user_model()
user_model.add_to_class(
    "following",
    models.ManyToManyField(
        "self", through=Contact, related_name="followers", symmetrical=False
    ),
)
