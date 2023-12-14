from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .models import Rose


class LatestRosesFeed(Feed):
    title = _("Roses ABC: Our latest rose varieties")
    link = reverse_lazy("roses:roses-list")
    description = _("New roses on Roses ABC")

    def items(self):
        return Rose.objects.order_by("-created").all()[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return truncatewords(item.description, 30)
