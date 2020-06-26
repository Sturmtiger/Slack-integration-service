from django.test import TestCase

from slack_integration.exceptions import (SlackApplicationNotFound,
                                          TemplateNotFound)
from ..slack_message_constructors import PostSlackMessageConstructor


class PostSlackMessageConstructorTest(TestCase):
    fixtures = ('dump.json',)

    def test_app_with_the_specified_name_does_not_exist(self):
        with self.assertRaises(SlackApplicationNotFound):
            PostSlackMessageConstructor(app_name='not_existing_name',
                                        template_name='qwerty',
                                        text='some text')

    def test_app_template_with_the_specified_name_does_not_exist(self):
        with self.assertRaises(TemplateNotFound):
            PostSlackMessageConstructor(app_name='my_app',
                                        template_name='qwerty',
                                        text='some text')

    def test_message_payload_is_dict(self):
        constructor = PostSlackMessageConstructor(app_name='my_app',
                                                  template_name='my_template',
                                                  text='some text')
        message_payload = constructor.get_message_payload()

        self.assertIsInstance(message_payload, dict)
