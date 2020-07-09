import json

import requests

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from django_celery_beat.models import PeriodicTask

from slack import WebClient
from slack.errors import SlackApiError

from slack_integration import models

from . import serializers
from .permissions import IsDeveloper
from .mixins.get_permissions import AdminDeveloperPermissionsMixin
from .mixins.get_serializer_class import GetSerializerClassListMixin
from .mixins.crontab_view import (RetrieveMixin, UpdateMixin, CreateMixin,
                                  DestroyMixin)
from .slack_web_client import CustomSlackWebClient


class SlackApplicationViewSet(AdminDeveloperPermissionsMixin,
                              GetSerializerClassListMixin,
                              ModelViewSet):
    queryset = models.SlackApplication.objects.all()
    serializer_class = serializers.SlackApplicationSerializer
    serializers_dict = {
        'list': serializers.SlackApplicationListSerializer,
    }


class TemplateViewSet(AdminDeveloperPermissionsMixin,
                      GetSerializerClassListMixin,
                      ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer
    serializers_dict = {
        'list': serializers.TemplateListSerializer,
    }


class TemplateCrontabView(RetrieveMixin,
                          UpdateMixin,
                          CreateMixin,
                          DestroyMixin,
                          AdminDeveloperPermissionsMixin,
                          generics.GenericAPIView):
    serializer_class = serializers.CrontabScheduleSerializer
    queryset = models.Template.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, *kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def _get_periodic_task_obj_if_exists(self, template_obj):
        app_name, template_name = self._get_periodic_task_name_data(
                                    template_obj).values()
        try:
            return PeriodicTask.objects.get(
                     name=f'{app_name} : {template_name}')
        except ObjectDoesNotExist:
            return None

    def _get_crontab_obj_if_periodic_task_exists(self, template_obj):
        periodic_task = self._get_periodic_task_obj_if_exists(template_obj)

        if periodic_task:
            return periodic_task.crontab

    def _get_periodic_task_name_data(self, template_obj):
        app_name = template_obj.application.name
        template_name = template_obj.name

        return {'app_name': app_name,
                'template_name': template_name}


class ActionsBlockViewSet(AdminDeveloperPermissionsMixin,
                          GetSerializerClassListMixin,
                          ModelViewSet):
    queryset = models.ActionsBlock.objects.all()
    serializer_class = serializers.ActionsBlockSerializer
    serializers_dict = {
        'list': serializers.ActionsBlockListSerializer,
    }


class ButtonViewSet(AdminDeveloperPermissionsMixin, ModelViewSet):
    queryset = models.Button.objects.all()
    serializer_class = serializers.ButtonSerializer


class CreateUpdateDestroySlackMessageView(APIView):
    """
    Works with the Slack API. Delegates requests to Slack API.
    """
    permission_classes = (IsDeveloper,)

    def post(self, request):
        serializer = serializers.PostMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_obj = get_object_or_404(models.SlackApplication,
                                  name=serializer.validated_data['app_name'])
        token = app_obj.bot_user_oauth_access_token

        slack_web_client = CustomSlackWebClient(token)

        try:
            slack_response = slack_web_client.chat_postMessage(**message)
            template = models.Template.objects.filter(
                thread_subscription=True,
                name=request.data['template_name'])
            # !!! name and app are unique together.
            # There is a mistake in the above code `template =`
            if template.exists():
                # if template subs flag is True, create a MessageTimeStamp
                # instance to track the thread for the message.
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

        # if the block_id is not None, then there was an interaction
        # with any button from the actions block
        if block_id:
            actions_block = models.ActionsBlock.objects.filter(
                                            action_subscription=True,
                                            block_id=block_id,)

            if actions_block.exists():
                callback_url = actions_block.get().callback_url
                # Q:should be asynchronous?
                requests.post(callback_url, json=request.data)

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
                template_callback_url = template.get().callback_url
                # Q:should be asynchronous?
                requests.post(template_callback_url, json=data)

        return Response(status=status.HTTP_200_OK, data=request.data)
