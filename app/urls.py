from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from app import views
from app import api

urlpatterns = patterns('',
    url(r'^$', views.HomePageView.as_view(), name='index'),
    url(r'^login/', views.LoginView.as_view(), name='login'),
    url(r'^logout/', views.LogoutView.as_view(), name='logout'),
    url(r'^social/', include('social_auth.urls')),
    url(r'^music_fetch/', views.music_fetch, name='music_fetch'),

    url(r'^api/userpic', api.GetUserpic.as_view(), name='api_userpic'),
    url(r'^api/song_url', api.GetSongUrl.as_view(), name='api_song_url'),
    url(r'^api/rate', api.Rate.as_view(), name='api_rate'),
    url(r'^api/characterise', api.ListenCharacterise.as_view(), name='api_characterise'),
    url(r'^api/recommend', api.Recommend.as_view(), name='api_recommend'),
)