from django.db import models
from plicata.books.models import Book


class Character(models.Model):
    name = models.CharField(max_length=80, unique=True)
    firstname = models.CharField(max_length=80,blank=True,null=True)
    lastname = models.CharField(max_length=80,blank=True,null=True)
    books = models.ManyToManyField(Book, blank=True,null=True, related_name='characters')
    bioshort = models.CharField(max_length=500,blank=True,null=True)
    biolong = models.TextField(blank=True,null=True)
    def __unicode__(self):
        return self.name

    class Meta:
        db_table='plicata_characters_characters'

class CharacterGroup(models.Model):
    """Groupings of characters, families being the perfect example, but used any time we want to refer to collections of persons rather than individual characters
    """
    groupname = models.TextField(max_length=80)
    grouptype = models.TextField(max_length=80)
    members = models.ManyToManyField(Character)
    def __unicode__(self):
        return self.groupname

    class Meta:
        db_table = 'plicata_characters_charactergroups'


class Nickname(models.Model):
    """A nickname given to a Character.   Characters may have more than one Nickname.  Not all nicknames are available to other characters (diminutives, enamoratives, etc.
    """
    nickname = models.TextField(max_length=80)
    character = models.ForeignKey(Character)
    description = models.TextField(max_length=255)
    moniker = models.NullBooleanField(default=None)  # eg 'Bob' for 'Robert'
    diminutive = models.NullBooleanField(default=None) # eg 'Carlita' for 'Carla'
    hypocoristic = models.NullBooleanField(default=None) # eg 'honey, dear, baby'
    derogatory = models.NullBooleanField(default=None) # eg 'Rat, Ass,Dickwad, Douche Bag
    familial = models.NullBooleanField(default=None) # eg Mom, Dad, Son, Cuz, Gramps
    physical = models.NullBooleanField(default=None) # eg Fatso, Red, Baldy
    personality = models.NullBooleanField(default=None) # eg Grumpy, Crazy, Drunken, Brainy, Dopey
    surname = models.NullBooleanField(default=None) # use of persons last name
    def __unicode__(self):
        return self.nickname

    class Meta:
        db_table='plicata_characters_nicknames'


class Relation(models.Model):
    character = models.ForeignKey(Character)
    relation = models.TextField(default='unknown')
    class Meta:
        db_table='plicata_charaters_relations'
