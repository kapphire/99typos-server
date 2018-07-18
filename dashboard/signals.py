import os
from django.db.models.signals import post_save
from django.dispatch import receiver

from dashboard.models import PageLink, ImageLink
from dashboard.tasks import get_link_validation_task, get_img_validation_task


# @receiver(post_save, sender=Site)
# def create_site(sender, created=False, **kwargs):
#     print(kwargs.get('instance'))
#     if created:
#         pass


# @receiver(post_save, sender=Page)
# def create_page(sender, created=False, **kwargs):
#     if created:
#         pass


# @receiver(post_save, sender=Content)
# def create_content(sender, created=False, **kwargs):
#     if created:
#         pass


@receiver(post_save, sender=PageLink)
def create_pg_link(sender, created=False, **kwargs):
    if created:
        obj = kwargs.get('instance')
        job_uid = get_link_validation_task.delay(id=obj.id).id
        obj.job_uid = job_uid
        obj.save()


@receiver(post_save, sender=ImageLink)
def create_img_link(sender, created=False, **kwargs):
    if created:
        obj = kwargs.get('instance')
        job_uid = get_img_validation_task.delay(id=obj.id).id
        obj.job_uid = job_uid
        obj.save()