from django.db import models

from plicata.books.models import Book

class Character(models.Model):
    book = models.ManyToManyField(Book)
    class Meta:
        abstract=True
