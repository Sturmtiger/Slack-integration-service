from slack import WebClient as SlackWebClient
from slack.errors import SlackApiError

from slack_integration import models

from .slack_message_constructors import (
                                PostSlackMessageConstructor,
                                UpdateSlackMessageConstructor,
                                )


class CustomSlackWebClient:
    def __init__(self, token: str):
        self._make_connection(token)

    def _make_connection(self, token):
        self.connection = SlackWebClient(token=token)

    def post_message(self, message_data: dict):
        post_message_constructor = PostSlackMessageConstructor(**message_data)
        message = post_message_constructor.get_message_payload()

        try:
            slack_response = self.connection.chat_postMessage(**message)
            template = models.Template.objects.filter(
                thread_subscription=True,
                name=request.data['template_name'])
            if template.exists():
                # if template subs flag is True, create a MessageTimeStamp
                # instance to track the thread for the message.
                template_obj = template.get()
                message_ts = slack_response.data['ts']
                models.MessageTimeStamp.objects.create(template=template_obj,
                                                       ts=message_ts)
        except SlackApiError as e:
            slack_response = e.response

    def update_message(self):
        pass

    def delete_message(self):
        pass
