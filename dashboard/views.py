from celery.result import AsyncResult

from django.contrib.auth import get_user_model

# Rest Framework
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from websites.models import Site
from websites.serializers import SiteListSerializer

User = get_user_model()

# Create your views here.
class CeleryTaskChecker(APIView):
    def post(self, request, format=None):
        # id = request.data.get('uniqueId')
        token = request.data.get('userToken')
        user = Token.objects.get(key=token).user
        sites = user.sites.filter(fill_status=False)
        response = {'status': 'finished', 'data': list()}
        for site in sites:
            # try:
            #     site = Site.objects.get(id=id)
            # except Exception as e:
            #     return Response({'status': 'error'})
            pages = site.pages.all()
            success_count = 0
            progress_count = 0

            for page in pages:
                job_uid = page.job_uid
                job_status = AsyncResult(job_uid).status

                if job_status != 'SUCCESS':
                    progress_count += 1
                else:
                    success_count += 1
            if success_count == len(pages):
                site.fill_status = True
                site.save()
            else:
                ratio = round(progress_count / len(pages), 2)
                response['status'] = 'checking'
                response['data'].append({'ratio': ratio, 'name': site.name})
        sites = user.sites
        serializer = SiteListSerializer(sites, many=True)
        response['sites'] = serializer.data
        return Response(response)


class CeleryTaskProgressChecker(APIView):
    def post(self, request, format=None):
        token = request.data.get('userToken')
        progress = request.data.get('progress')
        user = Token.objects.get(key=token).user
        # sites = user.sites.filter(task_status=False)
        sites = user.sites.all()
        result = list()

        for site in sites:
            detail = dict()
            detail['name'] = site.name
            detail['link'] = site.get_link_task_status
            detail['img'] = site.get_img_task_status

            if not detail['link'] and not detail['img']:
                continue

            elem = list()
            if detail['link']:
                elem_img = dict()
                elem_img['name'] = site.name
                elem_img.update(detail['link'])
                if elem_img:
                    elem.append(elem_img)

            if detail['img']:
                elem_link = dict()
                elem_link['name'] = site.name
                elem_link.update(detail['img'])
                if elem_link:
                    elem.append(elem_link)

            if elem:
                result.append(elem)
        sites = user.sites
        serializer = SiteListSerializer(sites, many=True)
        if not result:
            sites.update(task_status=True)
            return Response({'status': 'finished', 'data': result, 'sites': serializer.data})
        return Response({'status': 'in progress', 'data': result, 'sites': serializer.data})
