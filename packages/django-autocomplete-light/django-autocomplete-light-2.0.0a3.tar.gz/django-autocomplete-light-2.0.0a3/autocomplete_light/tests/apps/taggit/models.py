from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from taggit.managers import TaggableManager


@python_2_unicode_compatible
class Food(models.Model):
    name = models.CharField(max_length=100)
    tags = TaggableManager()

    def __str__(self):
        return self.name
