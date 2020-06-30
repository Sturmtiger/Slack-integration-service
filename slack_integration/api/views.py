from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import permissions

from slack import WebClient
from slack.errors import SlackApiError

from slack_integration import models

from slack_integration.api import serializers
from slack_integration.api.slack_message_constructors import (
                                PostSlackMessageConstructor,
                                UpdateSlackMessageConstructor,
                                )
from .permissions import IsAdmin, IsDeveloper


class SlackApplicationViewSet(ModelViewSet):
    queryset = models.SlackApplication.objects.all()
    serializer_class = serializers.SlackApplicationSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.SlackApplicationListSerializer

        return self.serializer_class

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            permissions_classes = (IsAdmin | IsDeveloper,)
        else:
            permissions_classes = (IsAdmin,)
        return (permission() for permission in permissions_classes)


class TemplateViewSet(ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.TemplateListSerializer

        return self.serializer_class

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            permissions_classes = (IsAdmin | IsDeveloper,)
        else:
            permissions_classes = (IsAdmin,)
        return (permission() for permission in permissions_classes)


class ActionsBlockViewSet(ModelViewSet):
    queryset = models.ActionsBlock.objects.all()
    serializer_class = serializers.ActionsBlockSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            permissions_classes = (IsAdmin | IsDeveloper,)
        else:
            permissions_classes = (IsAdmin,)
        return (permission() for permission in permissions_classes)


class ButtonViewSet(ModelViewSet):
    queryset = models.Button.objects.all()
    serializer_class = serializers.ButtonSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            permissions_classes = (IsAdmin | IsDeveloper,)
        else:
            permissions_classes = (IsAdmin,)
        return (permission() for permission in permissions_classes)


class CreateUpdateDestroySlackMessageView(APIView):
    """
    Works with the Slack API. Delegates requests to Slack API.
    """
    permission_classes = (IsDeveloper,)

    def post(self, request):
        serializer = serializers.PostMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_obj = models.SlackApplication.objects.get(
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
        serializer = serializers.UpdateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_obj = models.SlackApplication.objects.get(
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
        serializer = serializers.DeleteMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_obj = models.SlackApplication.objects.get(
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
        print(data)
        return Response(status=200, data=data)
