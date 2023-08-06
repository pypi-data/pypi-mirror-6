#-*- coding: utf-8 -*-
from __future__ import unicode_literals

#from django.test.testcases import TestCase

from likert_field.tests.utils_for_tests import CustomTestCase
#from likert_field.models import LikertField

from likert_test_app.models import SimpleUseModel


class SimpleUseModelTestCase(CustomTestCase):

    def setUp(self):
        pass

    def test_simple_use_case(self):
        print dir(SimpleUseModel)
        print type(SimpleUseModel)
        print(SimpleUseModel.objects.all())
        survey = SimpleUseModel.objects.create(test_is_the_best=5)
        response = SimpleUseModel.objects.get(pk=survey.pk)
        self.assertEqual(survey.test_is_the_best, response.test_is_the_best)
