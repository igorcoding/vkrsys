from django.conf.urls import patterns, url, include
from django.conf.urls.i18n import i18n_patterns

from app import views
from app.views import api

urlpatterns = patterns('',
    url(r'^(?P<username>\w+)?$', views.HomePageView.as_view(), name='home'),
    url(r'^about/', views.AboutView.as_view(), name='about'),
    url(r'^login/', views.LoginView.as_view(), name='login'),
    url(r'^logout/', views.LogoutView.as_view(), name='logout'),
    url(r'^music_fetch/', views.music_fetch, name='music_fetch'),
)