from django.db import models


class Author(models.Model):
    lastname = models.CharField(max_length=80)
    firstname = models.CharField(max_length=80)
    displayname = models.CharField(max_length=80, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    tagline = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='images', null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    visible = models.BooleanField()
    sortorder = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'plicata_authors'
        abstract = False

    class Admin:
        pass


    def __unicode__(self):
        return '%s %s' % (self.firstname, self.lastname)