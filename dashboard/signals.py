import os
from celery.exceptions import TimeoutError
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from websites.models import Site, PageLink, ImageLink
from dashboard.tasks import get_link_validation_task, get_img_validation_task


# @receiver(post_save, sender=Site)
# def create_site(sender, created=False, **kwargs):
#     if created:
#         print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


@receiver(post_save, sender=PageLink)
def create_pg_link(sender, created=False, **kwargs):
    if created:
        obj = kwargs.get('instance')
        task = get_link_validation_task.delay(id=obj.id)
        job_uid = task.id
        obj.job_uid = job_uid        
        obj.save()


@receiver(post_save, sender=ImageLink)
def create_img_link(sender, created=False, **kwargs):
    if created:
        obj = kwargs.get('instance')
        task = get_img_validation_task.delay(id=obj.id)
        job_uid = task.id
        obj.job_uid = job_uid
        obj.save()