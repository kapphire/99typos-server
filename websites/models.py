import uuid
import json
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from celery.result import AsyncResult

User = settings.AUTH_USER_MODEL

# Create your models here.
class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField('Website URL', max_length=255, null=False, blank=False, unique=True)
    name = models.CharField(max_length=100)
    sitemap = models.BooleanField(default=False)
    robots = models.BooleanField(default=False)
    fill_status = models.BooleanField(default=False)
    task_status = models.BooleanField(default=False)
    periodic_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, related_name='sites')

    @property
    def get_link_task_status(self):
        success = 0
        fails = 0
        links = self.links.filter(status=True)
        for link in links:
            job_status = AsyncResult(link.job_uid).status
            if job_status == 'SUCCESS':
                success += 1
            if job_status == 'FAILURE':
                fails += 1
            if link.job_uid == '':
                fails += 1
        count = len(links) - fails
        if success == count and success != 0:
            return False
        return {'success' : success, 'count' : count, 'label' : 'Links'}

    @property
    def get_img_task_status(self):
        success = 0
        fails = 0
        imgs = self.imgs.filter(status=True)
        for img in imgs:
            job_status = AsyncResult(img.job_uid).status
            if job_status == 'SUCCESS':
                success += 1
            if job_status == 'FAILURE':
                fails += 1
            if img.job_uid == '':
                fails += 1
        count = len(imgs) - fails
        if success == count and success != 0:
            return False
        return {'success' : success, 'count' : count, 'label' : 'Images'}

    def invalid_links(self):
        return self.links.filter(status=False)

    def invalid_imgs(self):
        return self.imgs.filter(status=False)

    def __str__(self):
        return self.url


class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.TextField('Website Page URL', null=False, blank=False, unique=True)
    job_uid = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    site = models.ForeignKey(Site, related_name='pages', on_delete=models.CASCADE)

    @property
    def to_dict(self):
        data = {
            'id': self.id,
            'url': self.url,
            'status': self.status,
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }
        return data
    
    def invalid_links(self):
        return self.links.filter(status=False)

    def invalid_imgs(self):
        return self.imgs.filter(status=False)

    def __str__(self):
        return self.url


class Content(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hashed = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    page = models.OneToOneField(Page, on_delete=models.CASCADE)

    @property
    def to_dict(self):
        data = {
            'id': self.id,
            'hashed': self.hashed,
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }
        return data
    
    def __str__(self):
        return self.hashed


class PageLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField('Page Link', max_length=600, null=False, blank=False, unique=True)
    job_uid = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    pages = models.ManyToManyField(Page, related_name='links', through='PageLinkAssociation')
    site = models.ForeignKey(Site, related_name='links', on_delete=models.CASCADE)


class PageLinkAssociation(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    link = models.ForeignKey(PageLink, on_delete=models.CASCADE)


class ImageLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField('Image Link', max_length=600, null=False, blank=False, unique=True)
    job_uid = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    pages = models.ManyToManyField(Page, related_name='imgs', through='ImageLinkAssociation')
    site = models.ForeignKey(Site, related_name='imgs', on_delete=models.CASCADE)


class ImageLinkAssociation(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    img = models.ForeignKey(ImageLink, on_delete=models.CASCADE)


class TyposGrammar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_message = models.CharField(max_length=255)
    offset = models.IntegerField()
    sentence = models.TextField(null=False, blank=False)
    length = models.IntegerField()
    message = models.CharField(max_length=255)
    issue_type = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)    
    content = models.ForeignKey(Content, related_name='typosgrammars' ,on_delete=models.CASCADE)

    @property
    def to_dict(self):
        data = {
            'id': self.id,
            'short_message': self.short_message,
            'offset': self.offset,
            'sentence': self.sentence,
            'length': self.length,
            'message': self.message,
            'issue_type': self.issue_type,
            'description': self.description,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
        }
        return data

    def __unicode__(self):
        return str(self.id)


class Replacement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    typos = models.ForeignKey(TyposGrammar, related_name='replacements', on_delete=models.CASCADE)
    
    @property
    def to_dict(self):
        data = {
            'id': self.id,
            'value': self.value,
            'created_at': self.created_at,
            'modified_at': self.modified_at
        }

    def __unicode__(self):
        return str(self.id)


