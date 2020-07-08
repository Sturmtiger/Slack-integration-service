import json

from django.db import transaction
from django.forms.models import model_to_dict

from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status

from django_celery_beat.models import PeriodicTask


class RetrieveMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        crontab_obj = self._get_crontab_obj_if_periodic_task_exists(instance)
        if not crontab_obj:
            error = {'crontab': 'crontab for this template does not exist'}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(crontab_obj)
        return Response(serializer.data)


class UpdateMixin(mixins.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        crontab_obj = self._get_crontab_obj_if_periodic_task_exists(
                        instance)
        if not crontab_obj:
            error = {'crontab': 'crontab for this template does not exist'}
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        if partial:
            cron_data = model_to_dict(crontab_obj, exclude=('id', 'timezone'))
            cron_data.update(**request.data.dict())
            serializer = self.get_serializer(data=cron_data)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        if serializer.validated_data == {}:
            error = {'crontab': 'crontab fields are not specified'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @transaction.atomic
    def perform_update(self, serializer):
        schedule = serializer.save()
        periodic_task_obj = self._get_periodic_task_obj_if_exists(
                                self.get_object())
        periodic_task_obj.crontab = schedule
        periodic_task_obj.save()


class CreateMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self._get_periodic_task_obj_if_exists(self.get_object()):
            error = {'crontab': 'crontab for this template already exists'}
            return Response(error, status=status.HTTP_403_FORBIDDEN)
        if serializer.validated_data == {}:
            error = {'crontab': 'crontab fields are not specified'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @transaction.atomic
    def perform_create(self, serializer):
        schedule = serializer.save()
        app_name, template_name = self._get_periodic_task_name_data(
                                    self.get_object()).values()
        PeriodicTask.objects.create(
            crontab=schedule,
            name='%s : %s' % (app_name, template_name),
            task='slack_integration.tasks.post_message',
            kwargs=json.dumps({'app_name': app_name,
                               'template_name': template_name})
        )


class DestroyMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        periodic_task_obj = self._get_periodic_task_obj_if_exists(instance)

        if not periodic_task_obj:
            error = {'crontab': 'crontab for this template does not exist'}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        self.perform_destroy(periodic_task_obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
