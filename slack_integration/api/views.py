from rest_framework.views import APIView
from rest_framework.response import Response
from slack.errors import SlackApiError

from .serializers import (PostMessageSerializer, UpdateMessageSerializer,
                          DeleteMessageSerializer)
from .slack_message_constructors import (PostSlackMessageConstructor,
                                         UpdateSlackMessageConstructor)
from .slack_connector import WebClient
from slack_integration.models import SlackApplication


class PostMessageView(APIView):
    def post(self, request):
        serializer = PostMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_obj = SlackApplication.objects.get(
            name=serializer.validated_data['app_name'])

        slack_web_client = WebClient(token=app_obj.bot_user_oauth_access_token)

        message_constructor = PostSlackMessageConstructor(
            **serializer.validated_data)
        message = message_constructor.get_message_payload()

        try:
            slack_response = slack_web_client.chat_postMessage(**message)
        except SlackApiError as e:
            slack_response = e.response

        return Response(slack_response.data,
                        status=slack_response.status_code)


class UpdateMessageView(APIView):
    def post(self, request):
        serializer = UpdateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_obj = SlackApplication.objects.get(
            name=serializer.validated_data['app_name'])

        slack_web_client = WebClient(token=app_obj.bot_user_oauth_access_token)

        message_constructor = UpdateSlackMessageConstructor(
            **serializer.validated_data)
        message = message_constructor.get_message_payload()

        try:
            slack_response = slack_web_client.chat_update(**message)
        except SlackApiError as e:
            slack_response = e.response

        return Response(slack_response.data,
                        status=slack_response.status_code)


class DeleteMessageView(APIView):
    def post(self, request):
        serializer = DeleteMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_obj = SlackApplication.objects.get(
            name=serializer.validated_data['app_name'])

        slack_web_client = WebClient(token=app_obj.bot_user_oauth_access_token)

        try:
            data = serializer.validated_data
            slack_response = slack_web_client.chat_delete(
                channel=data['channel'],
                ts=data['ts'])
        except SlackApiError as e:
            slack_response = e.response

        return Response(slack_response.data,
                        status=slack_response.status_code)
