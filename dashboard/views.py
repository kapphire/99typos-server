import os
import json
import requests
import shutil
import tldextract
from urllib.parse import urlparse
from celery.result import AsyncResult

# Django Libs
from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

# Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import Site, Page

# Serializers
from .serializers import (
    CreateSiteSerializer,
    PageDetailSerializer,
    PageListSerializer,
    ContentSerializer,
    UserSerializer,
    SiteListSerializer
)

# Scrapy
from scrapyd_api import ScrapydAPI

# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')

User = get_user_model()

# Create your views here.
class SiteRegister(APIView):
    permission_classes = (AllowAny,)
    serializer_class = CreateSiteSerializer

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
                'user': user.id,
                'sitemap': sitemap,
                'robots': robots
            }
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            site = serializer.create(data)
            domain = urlparse(site.url).netloc
            site_id = site.id
            # Delete Existing Assets            
            dirname = tldextract.extract(site.url).domain
            try:
                shutil.rmtree(os.path.join(dj_settings.BASE_DIR, 'assets', dirname))
            except Exception as e:
                print("Asset Folder Does Not Exist...")

            settings = {
                'unique_id': site_id,
                'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
            }
            task = scrapyd.schedule('default', 'icrawler', settings=settings, url=url, domain=domain)
            task = {
                'task_id': task,
                'unique_id': site_id,
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
        sites = user.sites.all()
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


class CeleryTaskChecker(APIView):
    def post(self, request, format=None):
        id = request.data.get('uniqueId')
        try:
            site = Site.objects.get(id=id)
        except Exception as e:
            return Response({'status': 'error'})
        pages = site.pages.all()
        links = site.all_pg_links
        imgs = site.all_img_links
        success_count = 0
        progress_count = 0

        for page in pages:
            job_uid = page.job_uid
            job_status = AsyncResult(job_uid).status

            if job_status != 'SUCCESS':
                progress_count += 1
            else:
                success_count += 1

        for link in links:
            job_uid = page.job_uid
            job_status = AsyncResult(job_uid).status

            if job_status != 'SUCCESS':
                progress_count += 1
            else:
                success_count += 1

        for img in imgs:
            job_uid = page.job_uid
            job_status = AsyncResult(job_uid).status

            if job_status != 'SUCCESS':
                progress_count += 1
            else:
                success_count += 1
        nums = len(pages) + len(links) + len(imgs)
        if success_count == nums:
            return Response({'status': 'finished'})
        else:
            ratio = round(progress_count / nums, 2)
            return Response({'status': 'checking', 'data': ratio})


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


class UserList(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, format=None):
        token = request.data.get('userToken')
        users = User.objects.all()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)