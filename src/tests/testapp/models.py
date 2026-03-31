"""Django models used exclusively by the test suite."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Company(models.Model):
    """A company that can employ ``Person`` instances."""

    name = models.CharField(max_length=30)
    public = models.BooleanField(default=False)


class PetStore(models.Model):
    """A pet store from which a ``Pet`` can be sold."""

    name = models.CharField(max_length=30)


class Person(models.Model):
    """A person who owns pets and is employed by a ``Company``."""

    name = models.CharField(max_length=30)
    hobbies = models.CharField(max_length=30)
    employer = models.ForeignKey(Company, on_delete=models.CASCADE)


class Pet(models.Model):
    """A pet owned by a ``Person`` and optionally sold from a ``PetStore``."""

    name = models.CharField(max_length=30)
    toys = models.CharField(max_length=30)
    species = models.CharField(max_length=30)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE)
    sold_from = models.ForeignKey(PetStore, null=True, on_delete=models.CASCADE)
    diet = models.CharField(max_length=200)


class TaggedItem(models.Model):
    """A generic tagged item pointing to any model via a ``GenericForeignKey``."""

    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')