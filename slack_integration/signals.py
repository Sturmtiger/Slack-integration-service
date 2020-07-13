from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from slack_integration.models import Template
from django_celery_beat.models import PeriodicTask


@receiver(pre_delete, sender=Template)
def clear_periodic_tasks(sender, instance, **kwargs):
    """
    If a template instance is deleting -
    delete the associated PeriodicTask instance if it exists.
    """
    name_pattern = f'template_id:{instance.id}'
    try:
        periodic_task = PeriodicTask.objects.get(name__endswith=name_pattern)
        periodic_task.delete()
    except ObjectDoesNotExist:
        pass
