from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authtoken.models import Token


class ViewSetActionsMixin:
    """
    Mixin for ViewSets, which allows to test
    `list` and `retrieve` actions.
    """

    def test_list_action(self):
        user = User.objects.get(username='admin')
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_action(self):
        user = User.objects.get(username='admin')
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(self.retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_action(self):
        user = User.objects.get(username='admin')
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.list_url,
                                    self.data['valid_data'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_action(self):
        user = User.objects.get(username='admin')
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.put(self.retrieve_url,
                                   self.data['valid_data'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_action(self):
        user = User.objects.get(username='admin')
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.patch(self.retrieve_url,
                                     self.data['valid_data_patch'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_action(self):
        user = User.objects.get(username='admin')
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.client.delete(self.retrieve_url)

        self.assertFalse(self.object in self.model.objects.all())
