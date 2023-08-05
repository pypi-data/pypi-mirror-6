from django.conf.urls import patterns, include, url
from django.contrib import admin

from mezzanine.core.views import direct_to_template

admin.autodiscover()

urlpatterns = patterns(
    url(r"^sellsheet/$", direct_to_template, {"template": "sellsheet.html"}, name="sellsheet"),
    url(r"^reviews/$", direct_to_template, {"template": "reviews.html"}, name="reviews"),
    url(r"^excerpts/$", direct_to_template, {"template": "excerpts.html"}, name="excerpts"),
    url(r"^chapters/$", direct_to_template, {"template": "chapters.html"}, name="chapters"),
    url(r"^outline/$", direct_to_template, {"template": "outline.html"}, name="outline"),
)
