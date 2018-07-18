# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
from dashboard.models import Site, Page, Content, ImageLink, PageLink
from dashboard.tasks import get_typos_task, insert_links_task, insert_images_task
from libs import get_hashed, ContentHandler

class CrawlerPipeline(object):
    def __init__(self, unique_id, *args, **kwargs):
        self.unique_id = unique_id

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            unique_id=crawler.settings.get('unique_id'),
        )

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        site = Site.objects.get(id=self.unique_id)
        if item['status'] == 200:
            page = Page(url=item['url'], site=site)
            page.save()

            hashed = get_hashed(item['body'])
            content = Content(hashed=hashed, page=page)
            content.save()

            job_uid = get_typos_task.delay(html=item['body'].decode('utf-8'), content_id=content.id).id
            page.job_uid = job_uid
            page.save()

            insert_links_task.delay(links=item['links'], page_id=page.id)
            insert_images_task.delay(imgs=item['imgs'], page_id=page.id)
        else:
            page = Page(url=item['url'], site=site, status=False)
            page.save()
        return item


# class CheckerPipeline(object):
#     def __init__(self, unique_id, *args, **kwargs):
#         self.unique_id = unique_id
#         self.pages = self.get_page_urls()

#     def get_page_urls(self, **kwargs):
#         pages = list()
#         self.site = Site.objects.get(id=self.unique_id)
#         for page in self.site.page_set.all():
#             pages.append(page.url)
#         return pages

#     @classmethod
#     def from_crawler(cls, checker):
#         return cls(
#             unique_id=checker.settings.get('unique_id'),
#         )

#     def close_spider(self, spider):
#         pass

#     def process_item(self, item, spider):
#         if item['status'] == 200 and item['url'] not in pages:
#             page = Page(url=item['url'], site=self.site)
#             page.save()

#             hashed = get_hashed(item['body'])
#             content_handler = ContentHandler(dirname=site.url, filename=str(page.id))
#             path = content_handler.get_file_path()
#             compress_status = content_handler.get_compressed(content=item['body'])

#             content = Content(hashed=hashed, path=path, page=page)
#             content.save()

#         if item['status'] ==200 and item['url'] in pages:
#             page = Page.objects.get(url=item['url'])
#             hashed = get_hashed(item['body'])

#             if page.content.hashed != hashed:
#                 page.modified_at = datetime.now()
#                 page.save()
#                 page.content.hashed = hashed
#                 page.content.modified_at = datetime.now()
#                 page.content.save()
#         return item