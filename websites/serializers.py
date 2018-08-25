import requests
from django.contrib.auth import password_validation as validators
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import serializers
from user_auth.models import User

from websites.models import Site, Page, PageLink, ImageLink, Content, TyposGrammar, Replacement
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
        content = obj.content
        typos = content.typosgrammars.filter(issue_type='misspelling')
        return len(typos)
    
    def get_grammar(self, obj):
        content = obj.content
        typos = content.typosgrammars.filter(issue_type='grammar')
        return len(typos)

    def get_link(self, obj):
        links = obj.links.filter(status=False)
        return len(links)

    def get_image(self, obj):
        imgs = obj.imgs.filter(status=False)
        return len(imgs)

class SiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Site
        fields = ('id', 'url', 'name', 'created_at', 'modified_at')

    def create(self, data):
        validated_data = {
            'url': data['url'],
            'name': data['name'],            
            'sitemap': data['sitemap'],
            'robots': data['robots']
        }
        site = Site.objects.create(**validated_data)
        return site


class SiteListSerializer(serializers.ModelSerializer):
    spelling = serializers.SerializerMethodField()
    grammar = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = ('id', 'url', 'name', 'spelling', 'grammar', 'image', 'link')

    def get_spelling(self, obj):
        count = 0
        pages = obj.pages.all()
        for page in pages:
            content = page.content
            typos = content.typosgrammars.filter(issue_type='misspelling')
            count += len(typos)
        return count

    def get_grammar(self, obj):
        count = 0
        pages = obj.pages.all()
        for page in pages:
            content = page.content
            typos = content.typosgrammars.filter(issue_type='grammar')
            count += len(typos)
        return count

    def get_link(self, obj):
        count = 0
        pages = obj.pages.all()
        for page in pages:
            links = page.links.filter(status=False)
            count += len(links)
        return count


    def get_image(self, obj):
        count = 0
        pages = obj.pages.all()
        for page in pages:
            imgs = page.imgs.filter(status=False)
            count += len(imgs)
        return count


class SiteLinkListSerializer(serializers.ModelSerializer):
    links = PageLinkListSerializer(many=True, read_only=True, source='invalid_links')

    class Meta:
        model = Site
        fields = ('id', 'name', 'url', 'links')


class SiteImageListSerializer(serializers.ModelSerializer):
    imgs = ImageLinkListSerializer(many=True, read_only=True, source='invalid_imgs')

    class Meta:
        model = Site
        fields = ('id', 'name', 'url', 'imgs')


class SiteDetailSerializer(serializers.ModelSerializer):
    pages = PageDetailSerializer(many=True)

    class Meta:
        model = Site
        fields = ('id', 'name', 'url', 'pages')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email')

class SiteUserSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True)

    class Meta:
        model = Site
        fields = ('id', 'name', 'url', 'users')