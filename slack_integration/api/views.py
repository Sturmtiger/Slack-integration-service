from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response

from slack import WebClient
from slack.errors import SlackApiError

from slack_integration.models import SlackApplication

from slack_integration.api.serializers import (PostMessageSerializer,
                                               UpdateMessageSerializer,
                                               DeleteMessageSerializer,
                                               SlackApplicationSerializer,)
from slack_integration.api.slack_message_constructors import (
                                PostSlackMessageConstructor,
                                UpdateSlackMessageConstructor,
                                )


class SlackApplicationViewSet(ModelViewSet):
    queryset = SlackApplication.objects.all()
    serializer_class = SlackApplicationSerializer
    # in progress


class CreateUpdateDestroySlackMessageView(APIView):
    """
    Works with the Slack API. Delegates requests to Slack API.
    """
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

    def put(self, request):
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

    def delete(self, request):
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


class InteractivityProcessingView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Receives payload of interactions with shortcuts, modals,
        or interactive components from Slack.

        More info:
        https://api.slack.com/apps/A014KJFJ7KR/interactive-messages
        """
        # in progress
        print('INTERACTIVITY')
        print(request.data['payload'])
        return Response(status=200)


class SlackEventsView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # in progress
        data = request.data
        print('EVENT')
        print(request.data)
        return Response(status=200, data=data)
