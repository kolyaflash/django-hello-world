"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client


class SimpleTest(TestCase):

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class HttpTest(TestCase):

    def test_home(self):
        c = Client()
        response = c.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello!')

    def test_requests(self):
        c = Client()
        response = c.get(reverse('requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Requests')


class CommonTest(TestCase):
    fixtures = ['initial_data.json',]

    def test_home_page(self):
        from django_hello_world.hello.models import MyData

        response = self.client.get(reverse('home'))
        profile = response.context["profile"]
        self.assertTrue('profile' in response.context)
        profile = response.context['profile']
        self.assertTrue(isinstance(profile, MyData))
        self.assertContains(response, profile.first_name)
        self.assertContains(response,
            profile.contacts_set.get(contact_type='email').value)

    def test_requests_logging(self):
        from django_hello_world.hello.models import RequestLog
        response = self.client.get(reverse('home'))
        self.assertEqual(RequestLog.objects.all().count(), 1)
        log = RequestLog.objects.all()[0]
        self.assertEqual(log.method, 'GET')
        self.assertEqual(log.path, reverse('home'))
        self.assertIsNotNone(log.date)
        self.assertIsNone(log.user)

    def test_request_page(self):
        response = self.client.get(reverse('requests'))
        self.assertTrue('requests' in response.context)
        self.assertEqual(len(response.context['requests']), 1)
