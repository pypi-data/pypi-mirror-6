from django.db import models
from plicata.books.models import Book
from mezzanine.core.fields import RichTextField

class Setting(models.Model):
    name = models.CharField(max_length=80, unique=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    setting = RichTextField(blank=True, null=True)
    books = models.ManyToManyField(Book)
    class Meta:
        db_table = 'plicta_setting_setting'
