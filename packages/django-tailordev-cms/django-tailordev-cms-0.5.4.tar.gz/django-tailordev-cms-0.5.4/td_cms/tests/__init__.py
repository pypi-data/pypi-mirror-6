# -*- coding: utf-8 -*-
"""
Models loaded for testing purpose
"""
from django.db import models
from mptt.fields import TreeManyToManyField

from ..models import Category


class Foo(models.Model):
    """
    Foo model is only defined here for testing purpose
    """
    title = models.CharField(max_length=200)
    categories = TreeManyToManyField(Category, related_name='foos',
                                     null=True, blank=True)
