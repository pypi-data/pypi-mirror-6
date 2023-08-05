"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import shortuuid

from six.moves.urllib.parse import urlparse

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import int_to_base36

from .models import OptOut
from .utils import invite, token_generator


class InviteTest(TestCase):
    def setUp(self):
        self.inviter = User.objects.create(username=shortuuid.uuid())
        self.existing = User.objects.create(username=shortuuid.uuid(),
                                            email='existing@example.com')

    def test_inviting(self):
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        self.assertFalse(user.is_active)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

        # Resend the mail
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        self.assertFalse(user.is_active)
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

        # Don't resend the mail
        user, sent = invite("foo@example.com", self.inviter, resend=False)
        self.assertFalse(sent)
        self.assertFalse(user.is_active)
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

        # Don't send the email to active users
        user, sent = invite("existing@example.com", self.inviter)
        self.assertFalse(sent)
        self.assertTrue(user.is_active)
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

    def test_views(self):
        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        url_parts = int_to_base36(user.id), token_generator.make_token(user)

        url = reverse('inviter2:register', args=url_parts)

        resp = self.client.get(url)

        self.assertEqual(200, resp.status_code, resp.status_code)

        resp = self.client.post(url, {'username': 'testuser',
                                      'email': 'foo@example.com',
                                      'new_password1': 'test-1234',
                                      'new_password2': 'test-1234'})

        self.assertEqual(302, resp.status_code, resp.content)

        self.client.login(username='testuser', password='test-1234')

        resp = self.client.get(reverse('inviter2:done'))

        self.assertEqual(200, resp.status_code, resp.status_code)

    def test_opt_out(self):
        self.assertEqual(2, User.objects.count())

        user, sent = invite("foo@example.com", self.inviter)
        self.assertTrue(sent)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(3, User.objects.count())

        url_parts = int_to_base36(user.id), token_generator.make_token(user)
        url = reverse('inviter2:opt-out', args=url_parts)

        resp = self.client.get(url)
        self.assertEqual(200, resp.status_code, resp.status_code)

        resp = self.client.post(url, {})
        self.assertEqual(302, resp.status_code, resp.status_code)
        self.assertEqual(reverse('inviter2:opt-out-done'),
                         urlparse(resp['Location']).path)
        self.assertEqual(2, User.objects.count())

        user, sent = invite("foo@example.com", self.inviter)
        self.assertFalse(sent)
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(1, OptOut.objects.count())
        self.assertTrue(OptOut.objects.is_blocked("foo@example.com"))
        self.assertIsNone(user)
