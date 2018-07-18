import requests
from django.contrib.auth import password_validation as validators
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import serializers
from user_auth.models import User

from .models import Site, Page, PageLink, ImageLink, Content, TyposGrammar, Replacement
from libs import *

User = get_user_model()


class ReplacementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Replacement
        fields = ('id', 'value',)


class TyposGrammarSerializer(serializers.ModelSerializer):
    replacements = ReplacementSerializer(many=True)

    class Meta:
        model = TyposGrammar
        fields = ('id', 'short_message', 'offset', 'sentence', 'length', 'message', 'issue_type', 'description', 'replacements')


class ContentSerializer(serializers.ModelSerializer):
    typosgrammars = TyposGrammarSerializer(many=True)

    class Meta:
        model = Content
        fields = ('id', 'hashed', 'typosgrammars')


class PageLinkListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PageLink
        fields = ('id', 'url', 'status')


class ImageLinkListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageLink
        fields = ('id', 'url', 'status')


class PageDetailSerializer(serializers.ModelSerializer):
    content = ContentSerializer()
    links = PageLinkListSerializer(many=True, read_only=True, source='invalid_links')
    imgs = ImageLinkListSerializer(many=True, read_only=True, source='invalid_imgs')

    class Meta:
        model = Page
        fields = ('id', 'url', 'content', 'links', 'imgs')


class PageListSerializer(serializers.ModelSerializer):
    spelling = serializers.SerializerMethodField()
    grammar = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ('id', 'url', 'spelling', 'grammar', 'image', 'link')

    def get_spelling(self, obj):
        count = 0
        content = obj.content
        typos = content.typosgrammars.all()
        for typo in typos:
            if typo.issue_type == 'misspelling':
                count += 1
            else:
                continue
        return count
    
    def get_grammar(self, obj):
        count = 0
        content = obj.content
        typos = content.typosgrammars.all()
        for typo in typos:
            if typo.issue_type == 'grammar':
                count += 1
            else:
                continue
        return count

    def get_image(self, obj):
        count = 0
        imgs = obj.imgs.all()
        for img in imgs:
            if img.status == False:
                count += 1
            else:
                continue
        return count

    def get_link(self, obj):
        count = 0
        links = obj.links.all()
        for link in links:
            if link.status == False:
                count += 1
            else:
                continue
        return count


class CreateSiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Site
        fields = ('id', 'url', 'name', 'created_at', 'modified_at', 'user')

    def create(self, data):
        validated_data = {
            'url': data['url'],
            'name': data['name'],
            'user': User.objects.get(id=data['user']),
            'sitemap': data['sitemap'],
            'robots': data['robots']
        }
        site = Site(**validated_data)
        site.save()
        return site


class UserSerializer(serializers.ModelSerializer):
    sites = CreateSiteSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'sites')


class SiteListSerializer(serializers.ModelSerializer):
    spelling = serializers.SerializerMethodField()
    grammar = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = ('id', 'url', 'name', 'created_at', 'modified_at', 'user', 'spelling', 'grammar', 'image', 'link')

    def get_spelling(self, obj):
        count = 0
        pages = obj.pages.all()
        for page in pages:
            content = page.content
            typos = content.typosgrammars.all()
            for typo in typos:
                if typo.issue_type == 'misspelling':
                    count += 1
                else:
                    continue
        return count

    def get_grammar(self, obj):
        count = 0
        pages = obj.pages.all()
        for page in pages:
            content = page.content
            typos = content.typosgrammars.all()
            for typo in typos:
                if typo.issue_type == 'grammar':
                    count += 1
                else:
                    continue
        return count

    def get_image(self, obj):
        count = 0
        pages = obj.pages.all()
        for page in pages:
            imgs = page.imgs.all()
            for img in imgs:
                if img.status == False:
                    count += 1
                else:
                    continue
        return count

    def get_link(self, obj):
        count = 0
        pages = obj.pages.all()
        for page in pages:
            links = page.links.all()
            for link in links:
                if link.status == False:
                    count += 1
                else:
                    continue
        return count
            