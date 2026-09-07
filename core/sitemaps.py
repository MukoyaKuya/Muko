from django.contrib.sitemaps import Sitemap

from django.urls import reverse

from .models import FeaturedProject, ShopCategory


class FeaturedProjectSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return FeaturedProject.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return ['home', 'shop_home']

    def location(self, item):
        return reverse(item)


class ShopCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return ShopCategory.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
