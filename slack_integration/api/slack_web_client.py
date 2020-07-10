from django.shortcuts import get_object_or_404

from slack import WebClient as SlackWebClient
from slack.errors import SlackApiError

from slack_integration import models

from .slack_message_constructors import (PostSlackMessageConstructor,
                                         UpdateSlackMessageConstructor,)


class CustomSlackWebClient:
    def __init__(self, app_name, template_name=None, channel_id=None):
        self.app_name = app_name
        self.template_name = template_name
        self.channel_id = channel_id

        self._prepare_data()

    def post_message(self, message_text=None):
        post_message_constructor = PostSlackMessageConstructor(
                                       self.template_obj,
                                       message_text)
        message = post_message_constructor.get_message_payload()

        try:
            slack_response = self.connection.chat_postMessage(**message)
            self._create_message_timestamp_if_subs(slack_response)
        except SlackApiError as e:
            slack_response = e.response

        return slack_response

    def update_message(self, message_text, ts):
        update_message_constructor = UpdateSlackMessageConstructor(
                                         self.template_obj,
                                         message_text,
                                         ts)
        message = update_message_constructor.get_message_payload()

        try:
            slack_response = self.connection.chat_update(**message)
        except SlackApiError as e:
            slack_response = e.response

        return slack_response

    def delete_message(self, ts):
        try:
            slack_response = self.connection.chat_delete(
                                 channel=self.channel_id,
                                 ts=ts)
        except SlackApiError as e:
            slack_response = e.response

        return slack_response

    def _create_message_timestamp_if_subs(self, slack_response):
        """
        Used to create a timestamp for a posted message if
        `thread_subscription` field = True.
        """
        if self.template_obj.thread_subscription:
            # if template subs flag is True, create a MessageTimeStamp
            # instance to keep track the thread under this message.
            message_ts = slack_response.data['ts']
            models.MessageTimeStamp.objects.create(
                template=self.template_obj,
                ts=message_ts)

    def _prepare_data(self):
        self._prepare_objects()
        self._make_connection()

    def _prepare_objects(self):
        self._prepare_application_obj()
        if self.template_name:
            self._prepare_template_obj()

    def _prepare_application_obj(self):
        self.app_obj = get_object_or_404(models.SlackApplication,
                                         name=self.app_name)

    def _prepare_template_obj(self):
        self.template_obj = get_object_or_404(models.Template,
                                              name=self.template_name,
                                              application=self.app_obj)

    def _make_connection(self):
        token = self.app_obj.bot_user_oauth_access_token
        self.connection = SlackWebClient(token=token)
