import sys
import os

from django.db import models
from django.db.models import permalink
from django.conf import settings
from plicata.authors.models import Author
from mezzanine.pages.models import Page
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged
from mezzanine.core.fields import FileField, RichTextField

class Site(models.Model):
    """ Site Model"""
    domain = models.CharField(max_length=100)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'django_site'
        managed = False

    class Admin:
        pass

    def __unicode__(self):
        return '%s' % self.domain

class Testing(models.Model):
    field1 = models.CharField(max_length=100)
    class Meta:
        abstract = True


class Genre(models.Model):
    """ Genre model """
    genre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'plicata_genres'
        ordering = ('genre',)
        managed = False
        abstract = False

    class Admin:
        pass

    def __unicode__(self):
        return '%s' % self.genre

    @permalink
    def get_absolute_url(self):
        return ('book_genre_detail', None, {'slug': self.slug})


class Publisher(models.Model):
    """ Publisher """
    publisher = models.CharField(max_length=100)
    prefix = models.CharField(max_length=20, blank=True)
    slug = models.SlugField(unique=True)
    website = models.URLField(blank=True)

    class Meta:
        db_table = 'plicata_publishers'
        ordering = ('publisher',)
        managed = True
        abstract = False

    class Admin:
        pass

    def __unicode__(self):
        return '%s' % self.full_title

    @property
    def full_title(self):
        return '%s %s' % (self.prefix, self.publisher)

    @permalink
    def get_absolute_url(self):
        return ('book_publisher_detail', None, {'slug': self.slug})


class Book(models.Model):
    """ Listing of books """
    title = models.CharField(max_length=255)
    prefix = models.CharField(max_length=20, blank=True)
    subtitle = models.CharField(blank=True, max_length=255)
    #slug = models.SlugField(unique=True)
    sites= models.ManyToManyField(Site, blank=True)
    authors = models.ManyToManyField(Author)
    author_text = models.CharField(max_length=100, blank=True, null=True)
    isbn = models.CharField(max_length=17, blank=True)
    pages = models.PositiveSmallIntegerField(blank=True, null=True, default=0)
    publisher = models.ForeignKey(Publisher, blank=True, null=True)
    published = models.DateField(blank=True, null=True)
    cost = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cover = models.FileField(upload_to='/books/images', blank=True)
    covericon = models.FileField(upload_to='/books/images', blank=True)
    sellsheet = models.FileField(upload_to='/books', blank=True)
    amazon = models.CharField(max_length=100, blank=True, null=True, default='')
    description = models.TextField(blank=True)
    blurb = RichTextField(blank=True)
    bigtext = RichTextField(blank=True,null=True)
    descriptionlong = models.TextField(blank=True)
    authornotes = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    visible = models.IntegerField(default=1)
    sortorder = models.IntegerField(default=99)

    class Meta:
        db_table = 'plicata_books'
        ordering = ('sortorder', 'title')
        managed = True
        abstract = False

    class Admin:
        list_display = ('title', 'pages')

    def __unicode__(self):
        return '%s' % self.full_title

    @property
    def full_title(self):
        if self.prefix:
            return '%s %s' % (self.prefix, self.title)
        else:
            return '%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('book_detail', None, {'slug': self.slug})

    @property
    def amazon_url(self):
        if self.isbn:
            try:
                return 'http://www.amazon.com/dp/%s/?%s' % (self.isbn, settings.AMAZON_AFFILIATE_EXTENTION)
            except:
                return 'http://www.amazon.com/dp/%s/' % self.isbn


class BookPage(Page):
    """A Mezzanine Page linked to a Plicata Book"""
    book = models.OneToOneField(Book)
    class Meta:
        db_table = 'pages_bookpage'
