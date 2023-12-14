import redis
from itertools import chain
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q, F
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from actions.utils import create_action
from .models import Rose, RoseComment, RosePhoto
from library.models import Article
from .serializers import UserSerializer, RoseSerializer, RoseAlternativeNameSerializer
from .forms import (
    EmailPostForm,
    RoseCommentForm,
    UpdateRoseCommentForm,
    AddRosePhotoForm,
    AddYoutubeVideoForm,
    EditRosePhotoForm,
)
from taggit.models import Tag
from .filters import RoseFilters, RoseDescriptionFilters
from .utils import resize_photo


# # connect to redispup
# r = redis.Redis(host=settings.REDIS_HOST,
#                 port=settings.REDIS_PORT,
#                 db=settings.REDIS_DB)


def home(request):
    # get rose ranking dictionary
    rose_ranking = r.zrange('rose_ranking', 0, -1, desc=True)[:9]
    rose_ranking_ids = [int(id) for id in rose_ranking]
    # get 10 most viewed roses
    # roses = Rose.objects.filter(id__in=rose_ranking_ids)
    roses = Rose.objects.filter(publish=True).order_by("-post_views")[:9]
    # get latest 3 articles
    articles = Article.objects.filter(publish=True).all()[:3]
    context = {"roses": roses, "articles": articles}
    return render(request, "roses/home.html", context)


# list of all roses chronologically
def roses_list(request, tag_slug=None):
    language = request.LANGUAGE_CODE

    roses_object = (
        Rose.objects.language(language).filter(publish=True).order_by("-created")
    )

    # filter rose_objects by tags if tag provided
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        roses_object = roses_object.filter(publish=True, tags__in=[tag])

    # paginate objects
    paginator = Paginator(roses_object, 12)
    page = request.GET.get("page")
    try:
        roses = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver only the first page
        roses = paginator.page(1)
    except EmptyPage:
        # if page is out of reange deliver the last page
        roses = paginator.page(paginator.num_pages)
    context = {"page": page, "roses": roses, "tag": tag}
    return render(request, "roses/post/roses_list.html", context)
