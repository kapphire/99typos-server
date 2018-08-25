import os
import requests
import shutil
import tldextract
from urllib.parse import urlparse

# Django Libs
from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

# Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .models import Site, Page

# Serializers
from .serializers import (
    SiteSerializer,
    PageDetailSerializer,
    PageListSerializer,
    SiteListSerializer,
    SiteLinkListSerializer,
    SiteImageListSerializer,
    SiteDetailSerializer,
    SiteUserSerializer
)
from users.serializers import UserSerializer

# Scrapy
from scrapyd_api import ScrapydAPI

# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')

User = get_user_model()

# Create your views here.
class SiteRegister(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SiteSerializer

    def get(self, request):
        task_id = request.GET.get('taskId', None)
        unique_id = request.GET.get('uniqueId', None)
        status = scrapyd.job_status('default', task_id)

        if status == 'finished':
            try:
                site = Site.objects.get(id=unique_id)
                pages = Page.objects.filter(site=site)
                resp = {
                    'status': 'finished',
                    'data': [page.to_dict for page in pages]
                }
                return Response(resp)
            except Exception as e:
                return Response({'status': 'error', 'data': str(e)})
        else:
            return Response({'status': 'crawling'})

    def post(self, request, format=None):
        url = request.data.get('url')
        name = request.data.get('name')
        token = request.data.get('userToken')
        sitemap = True if request.data.get('sitemap') == True else False
        robots = True if request.data.get('robots') == True else False
        user = Token.objects.get(key=token).user

        if user.is_verified:
            data = {
                'url': url,
                'name': name,
                'sitemap': sitemap,
                'robots': robots
            }
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            site = serializer.create(data)
            site.users.add(user)
            domain = urlparse(site.url).netloc
            settings = {
                'unique_id': site.id,
                'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
            }
            task = scrapyd.schedule('default', 'icrawler', settings=settings, url=url, domain=domain)
            task = {
                'task_id': task,
                'unique_id': site.id,
                'status': 'started'
            }
            resp = {
                'task': task,
                'data': serializer.data,
                'status': status.HTTP_201_CREATED
            }
            return Response(resp, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SiteList(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SiteListSerializer

    def post(self, request, format=None):
        token = request.data.get('userToken')
        user = Token.objects.get(key=token).user
        sites = user.sites
        serializer = self.serializer_class(sites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SiteCheck(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        token = request.data.get('userToken')
        url = request.data.get('url')
        val = URLValidator()
        status = False
        msg = ''
        user = Token.objects.get(key=token).user
        sites = [site.url for site in user.sites.all()]
        if url in sites:
            status = True
            msg = "Already exists."
        else:            
            try:
                val(url)
            except ValidationError as e:
                msg = list(e.messages)[0]
                status = True
                return Response({'data': msg, 'status': status})
            try:
                status_code = requests.get(url).status_code
                if status_code != 200:
                    msg = "{} error has occurred on your website".format(status_code)
            except Exception as e:
                msg = str(e)
                status = True
        return Response({'data': msg, 'status': status})


class PageList(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PageListSerializer

    def post(self, request, format=None):
        token = request.data.get('userToken')
        id = request.data.get('id')
        user = Token.objects.get(key=token).user
        site = Site.objects.get(id=id)
        pages = site.pages.all()
        serializer = self.serializer_class(pages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PageDetail(APIView):
    permission_classes = (AllowAny,)
    serializer_class = PageDetailSerializer

    def post(self, request, format=None):
        token = request.data.get('userToken')
        id = request.data.get('id')
        user = Token.objects.get(key=token).user
        page = Page.objects.get(id=id)
        content = page.content
        serializer = self.serializer_class(page)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangeSite(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SiteListSerializer
    
    def get_object(self, id):
        try:
            return Site.objects.get(id=id)
        except Site.DoesNotExist:
            raise Http404

    def put(self, request, id, format=None):
        site = self.get_object(id)
        site.name = request.data.get('name')
        site.url = request.data.get('url')
        token = request.data.get('userToken')
        site.save()
        user = Token.objects.get(key=token).user
        sites = user.sites.all()
        serializer = self.serializer_class(sites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id, format=None):
        site = self.get_object(id)
        token = request.data.get('userToken')
        user = Token.objects.get(key=token).user
        site.delete()
        sites = user.sites.all()
        serializer = self.serializer_class(sites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueGrammarList(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SiteDetailSerializer

    def post(self, request, format=None):
        token = request.data.get('userToken')
        user = Token.objects.get(key=token).user
        sites = user.sites.all()
        serializer = self.serializer_class(sites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueSpellingList(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SiteDetailSerializer

    def post(self, request, format=None):
        token = request.data.get('userToken')
        user = Token.objects.get(key=token).user
        sites = user.sites.all()
        serializer = self.serializer_class(sites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueLinkList(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SiteLinkListSerializer

    def post(self, request, format=None):
        token = request.data.get('userToken')
        user = Token.objects.get(key=token).user
        sites = user.sites.all()
        serializer = self.serializer_class(sites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueImageList(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SiteImageListSerializer

    def post(self, request, format=None):
        token = request.data.get('userToken')
        user = Token.objects.get(key=token).user
        sites = user.sites.all()
        serializer = self.serializer_class(sites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PermissionUserList(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        token = request.data.get('userToken')
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        user = Token.objects.get(key=token).user
        sites = user.sites.all()
        site_serializer = SiteUserSerializer(sites, many=True)
        return Response({'users': user_serializer.data, 'sites': site_serializer.data})


class PermissionUserAdd(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        token = request.data.get('userToken')
        site_id = request.data.get('siteId')
        user_id = request.data.get('userId')
        site = Site.objects.get(id=site_id)
        user = User.objects.get(id=user_id)
        site.users.add(user)
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        user = Token.objects.get(key=token).user
        sites = user.sites.all()
        site_serializer = SiteUserSerializer(sites, many=True)
        return Response({'users': user_serializer.data, 'sites': site_serializer.data})


class PermissionUserDelete(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        token = request.data.get('userToken')
        site_id = request.data.get('siteId')
        user_id = request.data.get('userId')
        site = Site.objects.get(id=site_id)
        user = User.objects.get(id=user_id)
        site.users.remove(user)
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        user = Token.objects.get(key=token).user
        sites = user.sites.all()
        site_serializer = SiteUserSerializer(sites, many=True)
        return Response({'users': user_serializer.data, 'sites': site_serializer.data})