import json

import requests

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from django_celery_beat.models import CrontabSchedule, PeriodicTask

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

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #
    # def perform_create(self, serializer):
    #     serializer.save()


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
        token = models.SlackApplication.objects.get(
                    name=serializer.validated_data['app_name']
                ).bot_user_oauth_access_token

        slack_web_client = WebClient(token=token)

        message_constructor = PostSlackMessageConstructor(
            **serializer.validated_data)
        message = message_constructor.get_message_payload()

        try:
            slack_response = slack_web_client.chat_postMessage(**message)
            template = models.Template.objects.filter(
                thread_subscription=True,
                name=request.data['template_name'])
            if template.exists():
                # if template subs flag is True, create a MessageTimeStamp
                # instance to track the thread for the message.
                # Q:should be asynchronous?
                template_obj = template.get()
                message_ts = slack_response.data['ts']
                models.MessageTimeStamp.objects.create(template=template_obj,
                                                       ts=message_ts)
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
                channel=data['channel_id'],
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
        """
        payload = request.data['payload']
        unpacked_interactivity_payload = json.loads(payload)
        block_id = unpacked_interactivity_payload['actions'][0].get('block_id')

        if block_id:
            actions_block = models.ActionsBlock.objects.filter(
                                            action_subscription=True,
                                            block_id=block_id,)

            # if a block_id is not None, then there was an interaction
            # with any button from the actions block
            if actions_block.exists():
                endpoint = actions_block.get().endpoint
                # Q:should be asynchronous?
                requests.post(endpoint, json=request.data)

        return Response(status=200)


class SlackEventsView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        thread_ts = data.get('event').get('thread_ts')

        # if an event is a thread message, the thread_ts is not None.
        if thread_ts:
            # get a template if its thread subs flag is True
            # and an object with the corresponding thread_ts exists.
            template = models.Template.objects.filter(
                        thread_subscription=True,
                        message_timestamps__ts=thread_ts)
            if template.exists():
                template_endpoint = template.get().endpoint
                # Q:should be asynchronous?
                requests.post(template_endpoint, json=data)

        return Response(status=status.HTTP_200_OK, data=request.data)
