from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from app import views

urlpatterns = patterns('',
    url(r'^$', views.HomePageView.as_view(), name='index'),
    url(r'^login/', views.LoginView.as_view(), name='login'),
    url(r'^logout/', views.LogoutView.as_view(), name='logout'),
    url(r'^social/', include('social_auth.urls')),

    url(r'^api/rate', views.Api.Rate.as_view(), name='api_rate'),
)