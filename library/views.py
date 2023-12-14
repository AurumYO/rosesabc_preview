from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _
from .models import ArticleCategory, Article, ArticlePhotos, Issue
from .forms import ContactForm


def library(request):
    language = request.LANGUAGE_CODE
    article_object = (
        Article.objects.language(language).filter(publish=True).order_by("-created")
    )

    paginator = Paginator(article_object, 10)
    page = request.GET.get("page")
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver only the first page
        articles = paginator.page(1)
    except EmptyPage:
        # if page is out of reange deliver the last page
        articles = paginator.page(paginator.num_pages)

    context = {"articles": articles, "page": page}
    return render(request, "library/library.html", context)
