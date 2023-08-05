from django.db import models
from plicata.books.models import Book


class Setting(models.Model):
    name = models.CharField(max_length=80, unique=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    books = models.ManyToManyField(Book)
    class Meta:
        db_table = 'plicta_settings_setting'