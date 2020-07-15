from slack import WebClient as SlackWebClient
from slack.errors import SlackApiError

from slack_integration import models

from .slack_message_constructors import (PostSlackMessageConstructor,
                                         UpdateSlackMessageConstructor,)


class CustomSlackWebClient:
    def __init__(self, app_obj, template_obj=None, channel_id=None,
                 post_message_constr_class=PostSlackMessageConstructor,
                 update_message_constr_class=UpdateSlackMessageConstructor,):

        self.post_message_constr_class = post_message_constr_class
        self.update_message_constr_class = update_message_constr_class

        self.app_obj = app_obj
        self.template_obj = template_obj
        self.channel_id = channel_id

        self._make_connection()

    def post_message(self, message_text=None):
        post_message_constructor = self.post_message_constr_class(
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
        update_message_constructor = self.update_message_constr_class(
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

    def _make_connection(self):
        token = self.app_obj.bot_user_oauth_access_token
        self.connection = SlackWebClient(token=token)
