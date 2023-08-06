
from django.db import models

from slugfield import SlugField


class Article(models.Model):
    name = models.CharField(max_length=100)
    slug = SlugField(populate_from='name')


class Article2(models.Model):
    name = models.CharField(max_length=100)
    slug = SlugField()


class Article3(models.Model):
    name = models.CharField(max_length=100)
    slug = SlugField(error_messages={'invalid': "It's custom error message"})