from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from ..slack_connector import WebClient
from ..slack_message_constructors import PostSlackMessageConstructor


class WebClientTest(TestCase):
    def test_singleton_pattern(self):
        """
        Checks that WebClient instance with the same token is not duplicated,
        but the existing one is reused.
        """
        x = WebClient(token='qwerty')
        y = WebClient(token='qwerty')

        self.assertIs(x, y)

    def test_problems_with_instatiantion(self):
        """
        Instantiating a WebClient with different tokens
        should result in different instances of the class.
        """
        x = WebClient(token='qwerty')
        y = WebClient(token='foobar')

        self.assertIsNot(x, y)


class PostSlackMessageConstructorTest(TestCase):
    fixtures = ('dump.json',)

    def test_app_with_the_specified_name_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist):
            PostSlackMessageConstructor(app_name='not_existing_name',
                                        template_name='qwerty',
                                        text='some text')

    def test_app_template_with_the_specified_name_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist):
            PostSlackMessageConstructor(app_name='my_app',
                                        template_name='qwerty',
                                        text='some text')

    def test_message_payload_is_dict(self):
        constructor = PostSlackMessageConstructor(app_name='my_app',
                                                  template_name='my_template',
                                                  text='some text')
        message_payload = constructor.get_message_payload()

        self.assertIsInstance(message_payload, dict)
