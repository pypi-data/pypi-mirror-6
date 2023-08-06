# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import User
from django.test import TestCase

from django_scim.filter import SCIMFilterTransformer, grammar


class FilterTest(TestCase):
    def setUp(self):
        self.erik = User.objects.create(
            username='erik',
            first_name='Erik',
            last_name='van Zĳst', # unicode
            email='erik.van.zijst@gmail.com',
            is_active=True,
            date_joined=datetime.datetime(2014, 1, 1))
        self.erik.save()
        self.erik.set_password('erik')
        self.erik.save()

        self.john = User.objects.create(
            username='john',
            first_name='John',
            last_name='Doe', # unicode
            email='john.doe@example.com',
            is_active=False,
            date_joined=datetime.datetime(2014, 2, 1))
        self.john.set_password('john')
        self.john.save()

        self.fred = User.objects.create(
            username='fred',
            is_active=True,
            date_joined=datetime.datetime(2014, 3, 1))
        self.fred.set_password('fred')
        self.fred.save()

    def testUsername(self):
        self.assertEqual(list(User.objects.filter(username='erik')),
                         list(SCIMFilterTransformer.search(u'username eq "erik"')))

    def testUnicode(self):
        pass

    def testCaseInsensitivity(self):
        pass

    def testOperatorPrecedence(self):

        parser = SCIMFilterTransformer()
        # parser.