from __future__ import absolute_import, unicode_literals
import requests

from libs import *
from celery.decorators import task
from urllib.parse import urlparse

from django.db import IntegrityError

from websites.models import *

from scrapyd_api import ScrapydAPI

scrapyd = ScrapydAPI('http://localhost:6800')


@task(name="get_typos")
def get_typos_task(**kwargs):
    html = kwargs.get('html', None)
    content = Content.objects.get(id=kwargs.get('content_id', None))
    soup = get_plain_text(html=html)
    text = get_filtered_text(soup=soup)
    typos = get_typos(text=text)

    for typo in typos:
        issue_type = typo['rule'].get('issueType', None)
        if issue_type == 'grammar' or issue_type == 'misspelling':
            punc_text = text.replace("’", "'")
            sentence = typo.get('sentence', None)
            position = punc_text.find(sentence.replace("’", "'"))
            offset = typo.get('offset', None)
            filtered_offset = offset - position

            typos_grammar = TyposGrammar()
            typos_grammar.short_message = typo.get('shortMessage', None)
            typos_grammar.offset = filtered_offset
            typos_grammar.sentence = sentence
            typos_grammar.length = typo.get('length', None)
            typos_grammar.message = typo.get('message', None)
            typos_grammar.issue_type = issue_type
            typos_grammar.description = typo['rule'].get('description', None)
            typos_grammar.content = content
            typos_grammar.save()

            replacements = typo.get('replacements', None)
            if replacements:
                for item in replacements:
                    replacement = Replacement()
                    replacement.value = item.get('value', None)
                    replacement.typos = typos_grammar
                    replacement.save()
        else:
            continue


@task(name='insert_links')
def insert_links_task(**kwargs):
    links = kwargs.get('links', None)
    page = Page.objects.get(id=kwargs.get('page_id', None))
    site = page.site
    for link in links:
        try:
            link_obj = PageLink.objects.create(url=link, site=site)
            PageLinkAssociation.objects.create(page=page, link=link_obj)
        except IntegrityError:
            link_obj = PageLink.objects.get(url=link, site=site)
            PageLinkAssociation.objects.create(page=page, link=link_obj)
        


@task(name='insert_images')
def insert_images_task(**kwargs):
    imgs = kwargs.get('imgs', None)
    page = Page.objects.get(id=kwargs.get('page_id', None))
    site = page.site
    for img in imgs:
        try:
            img_obj = ImageLink.objects.create(url=img, site=site)
            ImageLinkAssociation.objects.create(page=page, img=img_obj)
        except IntegrityError:
            img_obj = ImageLink.objects.get(url=img, site=site)
            ImageLinkAssociation.objects.create(page=page, img=img_obj)


@task(name="get_link_validation")
def get_link_validation_task(**kwargs):
    id = kwargs.get('id', None)
    obj = PageLink.objects.get(id=id)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        status = requests.get(obj.url, headers=headers).status_code
        if status != 200:
            obj.status = False
    except Exception as e:
        obj.status = False
    obj.save()


@task(name="get_img_validation")
def get_img_validation_task(**kwargs):
    id = kwargs.get('id', None)
    obj = ImageLink.objects.get(id=id)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        status = requests.get(obj.url, headers=headers).status_code
        if status != 200:
            obj.status = False
    except Exception as e:
        obj.status = False
    obj.save()


@task(name="sum_two_numbers")
def add(x):
    print('==========')
    return x + x


# @task(name="multiply_two_numbers")
# def mul(x, y):
#     total = x * (y * random.randint(3, 100))
#     return total


# @task(name="sum_list_numbers")
# def xsum(numbers):
#     return sum(numbers)

# @task(name='page_checker')
# def check_page(*args, **kwargs):
#     sites = Site.objects.all()
#     for site in sites:
#         domain = urlparse(site.url).netloc
#         settings = {
#             'unique_id': site.id,
#             'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
#         }
#         task = scrapyd.schedule('default', 'ichecker', settings=settings, url=site.url, domain=domain)