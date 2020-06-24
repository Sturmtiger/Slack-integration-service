from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status


class CreateUpdateDestroySlackMessageViewTest(APITestCase):
    fixtures = ('dump.json',)
    tested_url = reverse('slack-message')

    def test_not_developer_does_not_have_access(self):
        user = User.objects.get(username='admin')
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        post_response = self.client.post(self.tested_url)
        self.assertEqual(post_response.status_code,
                         status.HTTP_403_FORBIDDEN)

        put_response = self.client.put(self.tested_url)
        self.assertEqual(put_response.status_code,
                         status.HTTP_403_FORBIDDEN)

        delete_response = self.client.delete(self.tested_url)
        self.assertEqual(delete_response.status_code,
                         status.HTTP_403_FORBIDDEN)
