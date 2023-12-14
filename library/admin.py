from django.contrib import admin
from .models import Plant, Issue, ArticleCategory, Article, ArticlePhotos, Contact
from parler.admin import TranslatableAdmin, TranslatableTabularInline


class ArticlePhotoAdmin(TranslatableTabularInline):
    model = ArticlePhotos
    list_display = ["title", "alt_title", "article", "section_number"]
    fields = ("title", "alt_title", "article", "section_number", "photo")
    extra = 0


@admin.register(Article)
class Article(TranslatableAdmin):
    # set up fields for display in admin
    list_display = ["title", "author", "category", "created"]
    # order of filling the filds
    fields = (
        "title",
        "title_description",
        "short_description",
        "body_1",
        "body_2",
        "body_3",
        "body_4",
        "summary",
        "author",
        "slug",
        "category",
        "tags",
        "issue_id",
        "publish",
    )

    inlines = [ArticlePhotoAdmin]

    list_filter = ["created", "translations__title", "author", "category", "issue_id"]
    # set up search fields
    search_fields = ("translations__title",)

    # prepopulate slug fields
    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("title",)}