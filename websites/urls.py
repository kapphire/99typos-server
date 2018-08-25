from django.urls import path, include
from rest_framework import routers
from websites import views

router = routers.DefaultRouter()

urlpatterns = [
    path('site/register/', views.SiteRegister.as_view(), name='site-register'),
    path('site/list/', views.SiteList.as_view(), name='site-list'),
    path('site/check/', views.SiteCheck.as_view(), name='site-check'),
    path('site/change/<uuid:id>', views.ChangeSite.as_view(), name='change-site'),
    path('page/list/', views.PageList.as_view(), name='page-list'),
    path('page/detail/', views.PageDetail.as_view(), name='page-detail'),
    path('issue/grammar/', views.IssueGrammarList.as_view(), name='issue-grammar-list'),
    path('issue/spelling/', views.IssueSpellingList.as_view(), name='issue-spelling-list'),
    path('issue/link/', views.IssueLinkList.as_view(), name='issue-link-list'),
    path('issue/image/', views.IssueImageList.as_view(), name='issue-image-list'),
    path('permission/data/', views.PermissionUserList.as_view(), name='permission-user-list'),
    path('permission/user/add/', views.PermissionUserAdd.as_view(), name='permission-user-add'),
    path('permission/user/delete/', views.PermissionUserDelete.as_view(), name='permission-user-delete'),
]