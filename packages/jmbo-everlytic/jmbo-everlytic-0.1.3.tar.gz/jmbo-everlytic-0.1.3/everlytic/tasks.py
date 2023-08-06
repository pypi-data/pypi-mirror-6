from django.core.exceptions import ObjectDoesNotExist
from celery import task

from foundry.models import Member
from everlytic import api


@task(max_retries=3)
def subscribe_user(member_id, profile_class):
    try:
        instance = Member.objects.get(pk=member_id)
    except ObjectDoesNotExist:
        raise subscribe_user.retry()
    ep, created = profile_class.objects.get_or_create(member=instance)
    if created and instance.email:
        everlytic_id = api.subscribeUser(
            instance.last_name,
            instance.first_name,
            instance.email,
            instance.receive_email,
            everlytic_id=ep.everlytic_id)
        if everlytic_id is None:
            raise subscribe_user.retry()
        ep.everlytic_id = everlytic_id
        ep.save()


@task(max_retries=3)
def delete_user(everlytic_id):
    success = api.deleteEverlyticUser(everlytic_id)
    if not success:
        raise delete_user.retry()
