from django.db import models
from plicata.characters.models import Character, CharacterGroup


class Plot(models.Model):
    name = models.CharField(max_length=80)
    tagline = models.CharField(max_length=80)
    description = models.TextField(blank=True,null=True)
    characters = models.ManyToManyField(Character,blank=True,null=True)
    character_groups = models.ManyToManyField(CharacterGroup, blank=True, null=True)
    class Meta:
        db_table = 'plicata_plotlines_plotline'
