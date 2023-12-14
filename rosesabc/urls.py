from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from roses.sitemaps import RoseSitemap
from roses.views import home


sitemaps = {
    "roses": RoseSitemap,
}


urlpatterns = [
    re_path(r"^$", home, name="home_no_lang"),
]


urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("rosetta/", include("rosetta.urls")),
    path("account/", include("account.urls")),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", include("roses.urls", namespace="roses")),
)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
