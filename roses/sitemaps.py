from itertools import chain
from django.contrib.sitemaps import Sitemap
# from .models import Rose, RoseAlternativeName, RosePhoto, RoseYoutubeVideo


class RoseSitemap(Sitemap):
    # i18n = True
    # changefreq = "daily"
    # priority = 0.5

    # def items(self):
    #     roses_en = Rose.objects.language("en").all()
    #     roses_uk = Rose.objects.language("uk").all()
    #     alternative_uk_named_roses = RoseAlternativeName.objects.language("uk").all()
    #     alternative_en_named_roses = RoseAlternativeName.objects.language("en").all()
    #     rose_photos = RosePhoto.objects.all()
    #     # print(alternative_en_named_roses, alternative_uk_named_roses)
    #     return list(
    #         chain(
    #             roses_en,
    #             roses_uk,
    #             alternative_en_named_roses,
    #             alternative_uk_named_roses,
    #             rose_photos,
    #         )
    #     )

    # # update the last values of the sitemaps
    # def lastmod(self, obj):
    #     return obj.updated

    pass