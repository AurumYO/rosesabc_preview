from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    """
    Form for user registration.

    Attributes:
        password (CharField): Field for entering the user's password.
        password2 (CharField): Field for repeating and confirming the user's password.
        check_agree_terms_and_services (BooleanField): Field for confirming the agreement to terms and services.

    Meta:
        model (User): Specifies the model associated with this form.
        fields (Tuple): Specifies the fields from the model to include in the form.

    Methods:
        clean_password2(): Validates that the entered passwords match.

    Usage:
        Instantiate this form in your view and include it in the template to handle user registration.
    """

    password = forms.CharField(label=_("Passwrod"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Repeat Passwrod"), widget=forms.PasswordInput)
    check_agree_terms_and_services = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "email")

    def clean_password2(self):
        """
        Validates that the entered passwords match.

        Raises:
            forms.ValidationError: If the passwords don't match.

        Returns:
            str: The repeated password if validation is successful.
        """
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError(_("Passwords don't match"))
        return cd["password2"]


class UserEditForm(forms.ModelForm):
    """
    Form for editing user information.

    Meta:
        model (User): Specifies the model associated with this form.
        fields (Tuple): Specifies the fields from the model to include in the form.

    Usage:
        Instantiate this form in your view and include it in the template to handle user profile editing.
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ProfileEditForm(forms.ModelForm):
    """
    Form for editing user profile information.

    Meta:
        model (Profile): Specifies the model associated with this form.
        fields (Tuple): Specifies the fields from the model to include in the form.

    Usage:
        Instantiate this form in your view and include it in the template to handle user profile editing.
    """
    
    class Meta:
        model = Profile
        fields = ("date_of_birth", "region", "photo", "about_me")