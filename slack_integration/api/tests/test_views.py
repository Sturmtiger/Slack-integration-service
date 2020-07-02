from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from slack_integration.models import (SlackApplication, Template,
                                      ActionsBlock, Button)

from .mixins import ViewSetActionsMixin


class SlackApplicationViewSetTest(ViewSetActionsMixin, APITestCase):
    fixtures = ('dump.json',)
    model = SlackApplication
    object = model.objects.first()
    list_url = reverse('slackapplication-list')
    retrieve_url = reverse('slackapplication-detail',
                           args=(object.pk,))
    data = {
        # for POST and PUT methods
        'valid_data': {
            'name': 'some_application',
            'signing_secret': 'j62ZdsDbccZiJSV30mknv1nTxHEdbczX',
            'bot_user_oauth_access_token': 'vUCIBtfyGtbUwVUcsRwH3IX'
                                           '48pd1TZKhMDJLd8fWCNiAK1'
                                           'SCNrgN0hexa'
        },
        'valid_data_patch': {
            'name': 'new name'
        }
    }


class TemplateViewSetTest(ViewSetActionsMixin, APITestCase):
    fixtures = ('dump.json',)
    model = Template
    object = model.objects.first()
    list_url = reverse('template-list')
    retrieve_url = reverse('template-detail',
                           args=(object.pk,))
    data = {
        # for POST and PUT methods
        'valid_data': {
            'application': SlackApplication.objects.last().pk,
            'name': 'some_template',
            'channel_name': 'C32141CDE',
            'message_text': 'Some message text',
            'fallback_text': 'Some fallback text',
            'thread_subscription': True,
            'endpoint': 'https://postman-echo.com/post'
        },
        'valid_data_patch': {
            'thread_subscription': True
        },
    }

    # DOESNT WORK
    # def test_subs_is_false_when_endpoint_is_empty(self):
    #     user = User.objects.get(username='admin')
    #     token = Token.objects.get_or_create(user=user)[0]
    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    #
    #     data = {
    #         'thread_subscription': True,
    #         'endpoint': 'https://postman-echo.com/post'
    #     }
    #     self.client.patch(self.retrieve_url, data)
    #     self.client.patch(self.retrieve_url, {'endpoint': ''})
    #     self.assertEqual(self.object.thread_subscription, False)


class ActionsBlockViewSetTest(ViewSetActionsMixin, APITestCase):
    fixtures = ('dump.json',)
    model = ActionsBlock
    object = model.objects.first()
    list_url = reverse('actionsblock-list')
    retrieve_url = reverse('actionsblock-detail',
                           args=(object.pk,))
    data = {
        # for POST and PUT methods
        'valid_data': {
            'template': Template.objects.get(pk=7).pk,
            'block_id': 'some_block_id',
            'action_subscription': True,
            'endpoint': 'https://postman-echo.com/post'
        },
        'valid_data_patch': {
            'block_id': 'new_block_id'
        },
    }

    def test_template_cannot_have_more_than_1_actions_block(self):
        user = User.objects.get(username='admin')
        token = Token.objects.get_or_create(user=user)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.client.post(self.list_url,
                         self.data['valid_data'])

        # data with new block_id (because the block_id is an unique field)
        self.data['valid_data']['block_id'] = 'new_block_id232'
        response = self.client.post(self.list_url,
                                    self.data['valid_data'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ButtonViewSetTest(ViewSetActionsMixin, APITestCase):
    fixtures = ('dump.json',)
    model = Button
    object = model.objects.first()
    list_url = reverse('button-list')
    retrieve_url = reverse('button-detail',
                           args=(object.pk,))
    data = {
        # for POST and PUT methods
        'valid_data': {
            'actions_block': ActionsBlock.objects.last().pk,
            'action_id': 'g3Fq5gdvz',
            'text': 'button text'
        },
        'valid_data_patch': {
            'text': 'new button text'
        },
    }


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
