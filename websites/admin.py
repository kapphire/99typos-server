from django.contrib import admin
from .models import *

# Register your models here.
class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url', 'sitemap', 'robots', 'created_at', 'modified_at')


class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'site', 'url', 'job_uid', 'status', 'created_at', 'modified_at')


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'page', 'hashed', 'created_at', 'modified_at')


class PageLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'job_uid', 'status')


class ImageLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'job_uid', 'status')


class PageLinkAssociationAdmin(admin.ModelAdmin):
    list_display = ('page', 'link')


class ImageLinkAssociationAdmin(admin.ModelAdmin):
    list_display = ('page', 'img')


class TyposGrammarAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_message', 'offset', 'sentence', 'length', 'message', 'issue_type', 'description', 'content', 'created_at', 'modified_at')


class ReplacementAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'created_at', 'modified_at')


admin.site.register(Site, SiteAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(PageLink, PageLinkAdmin)
admin.site.register(ImageLink, ImageLinkAdmin)
admin.site.register(PageLinkAssociation, PageLinkAssociationAdmin)
admin.site.register(ImageLinkAssociation, ImageLinkAssociationAdmin)
admin.site.register(TyposGrammar, TyposGrammarAdmin)
admin.site.register(Replacement, ReplacementAdmin)