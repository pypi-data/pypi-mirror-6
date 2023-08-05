from django.db import models
from plicata.books.models import Book
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged
from mezzanine.core.fields import FileField, RichTextField

class Review(models.Model):
    book = models.ForeignKey(Book)
    visible = models.BooleanField(default=True)
    sortorder = models.IntegerField(default=999)
    reviewer = models.TextField(max_length=80)
    entity = models.TextField(blank=True, max_length=80)
    citation = models.TextField(blank=True, max_length=255)
    url = models.URLField(blank=True)
    body = RichTextField()

class Quote(models.Model):
    review = models.ForeignKey(Review)
    visible = models.BooleanField(default=True)
    sortorder = models.IntegerField(default=999)
    quote = RichTextField()

#test