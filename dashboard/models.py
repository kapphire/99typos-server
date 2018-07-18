import uuid
import json
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL

# Create your models here.
class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField('Website URL', max_length=255, null=False, blank=False, unique=True)
    name = models.CharField(max_length=100)
    sitemap = models.BooleanField(default=False)
    robots = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='sites', on_delete=models.CASCADE)

    @property
    def all_img_links(self):
        data = list()
        pages = self.pages.all()
        for page in pages:
            [data.append(img.url) for img in page.imgs.all()]
        data = list(set(data))
        return data

    @property
    def all_pg_links(self):
        data = list()
        pages = self.pages.all()
        for page in pages:
            [data.append(link.url) for link in page.links.all()]
        data = list(set(data))
        return data

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
        return PageLink.objects.filter(status=False)

    def invalid_imgs(self):
        return ImageLink.objects.filter(status=False)

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
    url = models.CharField('Page Link', max_length=600, null=False, blank=False)
    job_uid = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    page = models.ForeignKey(Page, related_name='links', on_delete=models.CASCADE)


class ImageLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField('Image Link', max_length=600, null=False, blank=False)
    job_uid = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    page = models.ForeignKey(Page, related_name='imgs', on_delete=models.CASCADE)


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


