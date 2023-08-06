import logging
from django.contrib.sitemaps import Sitemap

from models import Place

# Instantiate logger.
logger = logging.getLogger(__name__)


class PlaceSitemap(Sitemap):
    """
    Sitemap settings for Places.
    """
    def items(self):
        return Place.objects.filter(active=True)