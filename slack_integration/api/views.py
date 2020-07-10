import json

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from django_celery_beat.models import PeriodicTask

from slack_integration import models
from slack_integration.tasks import post_request

from . import serializers
from .permissions import IsDeveloper
from .mixins.views.get_permissions import AdminDeveloperPermissionsMixin
from .mixins.views.get_serializer_class import GetSerializerClassListMixin
from .mixins.views.crontab_view import (RetrieveMixin, UpdateMixin,
                                        CreateMixin, DestroyMixin)
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

        valid_data = serializer.validated_data

        slack_web_client = CustomSlackWebClient(
                               valid_data['app_name'],
                               valid_data['template_name'])

        slack_response = slack_web_client.post_message(valid_data['text'])

        return Response(slack_response.data,
                        status=slack_response.status_code)

    def put(self, request):
        serializer = serializers.UpdateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        valid_data = serializer.validated_data

        slack_web_client = CustomSlackWebClient(
                               valid_data['app_name'],
                               valid_data['template_name'])

        slack_response = slack_web_client.update_message(valid_data['text'],
                                                         valid_data['ts'])

        return Response(slack_response.data,
                        status=slack_response.status_code)

    def delete(self, request):
        serializer = serializers.DeleteMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        valid_data = serializer.validated_data

        slack_web_client = CustomSlackWebClient(
                               valid_data['app_name'],
                               channel_id=valid_data['channel_id'])

        slack_response = slack_web_client.delete_message(valid_data['ts'])

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
            try:
                actions_block_obj = models.ActionsBlock.objects.get(
                                        action_subscription=True,
                                        block_id=block_id)
                callback_url = actions_block_obj.callback_url
                post_request.delay(callback_url, request.data)
            except ObjectDoesNotExist:
                pass

        return Response(status=status.HTTP_200_OK)


class SlackEventsView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        thread_ts = data.get('event').get('thread_ts')

        # if an event is a thread message, the thread_ts is not None.
        if thread_ts:
            # get a template if its thread subs flag is True
            # and an object with the corresponding thread_ts exists.
            try:
                template_obj = models.Template.objects.get(
                               thread_subscription=True,
                               message_timestamps__ts=thread_ts)
                callback_url = template_obj.callback_url
                post_request.delay(callback_url, data)
            except ObjectDoesNotExist:
                pass

        return Response(status=status.HTTP_200_OK, data=request.data)
