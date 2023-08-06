from django.db import models

from likert_field.models import LikertField


class SimpleUseModel(models.Model):
    subject = models.CharField(max_length=15)
    test_is_the_best = LikertField()


class ParametersModel(models.Model):
    item = LikertField('Test is the best')
