from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _
from actions.utils import create_action
from actions.models import Action
from .models import Profile, Terms, Contact
from .forms import LoginForm, UserEditForm, ProfileEditForm, UserRegistrationForm
from roses.models import Rose, RosePhoto
from library.models import Article



# Log out user
@login_required
def dashboard(request):
    user = request.user
    language = request.LANGUAGE_CODE
    
    # Display all actions by default
    actions = Action.objects.exclude(user=user)

    following_ids = user.following.values_list("id", flat=True)
    if following_ids:
        # if user is following others, retrive only their accounts
        actions = actions.filter(user_id__in=following_ids)

    actions = actions.select_related("user", "user__profile").prefetch_related(
        "target"
    )[:10]

    # obtain total number of added Rose descriptions, Pictures added
    rose_added = Rose.objects.filter(post_author=user).count()
    images_added = RosePhoto.objects.filter(picture_author=user).count()
    articles_added = Article.objects.filter(author=user).count()
    liked_roses = user.roses_liked.count()

    context = {
        "section": "dashboard",
        "actions": actions,
        "images_added": images_added,
        "rose_added": rose_added,
        "articles_added": articles_added,
        "liked_roses": liked_roses,
    }

    return render(request, "account/dashboard.html", context)


# Login user
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse(_("Authenticated sucessfully"))
                else:
                    return HttpResponse(_("Invalid login"))
    else:
        form = LoginForm()
    context = {"form": form}
    return render(request, "account/login.html", context)


# Registration of the new User
def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        user_name = user_form.data.get("username")
        # Check if a user with the same username already exists
        if User.objects.filter(username=user_name).exists():
            messages.warning(
                request,
                _(
                    f'There is already a registered user with the username "{user_name}". Please select another username.'
                ),
            )
        else:
            if user_form.is_valid():
                # create new user object without saving it to the db yet
                new_user = user_form.save(commit=False)
                # set enterred password
                new_user.set_password(user_form.cleaned_data["password"])
                # save the User object
                new_user.save()
                Profile.objects.create(user=new_user)
                # make a record that user had agreed on terms and services and on privacy policy
                if user_form.cleaned_data["check_agree_terms_and_services"] == True:
                    Terms.objects.create(user_id=new_user, is_active=True)
                create_action(new_user, _(" has created an account"))
                return render(
                    request, "account/register_done.html", {"new_user": new_user}
                )
    else:
        user_form = UserRegistrationForm()
    return render(request, "account/register.html", {"user_form": user_form})


# Edit user info
@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():
            if User.objects.filter(email=user_form.data.get("email")).exists():
                form_email = user_form.data.get("email")
                email_owner = User.objects.get(email=form_email)
                if request.user.username != email_owner.username:
                    messages.error(
                        request,
                        _(
                            f"Email {form_email} already taken. Please use another email."
                        ),
                    )
                    return HttpResponseRedirect(reverse("edit"))
            user_form.save()
            profile_form.save()
            messages.success(request, _("Profile updated successfully"))
            return HttpResponseRedirect(reverse("dashboard"))
        else:
            messages.error(request, _("Error updating your profile"))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {"user_form": user_form, "profile_form": profile_form}
    return render(request, "account/edit.html", context)

