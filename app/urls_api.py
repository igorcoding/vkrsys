from django.conf.urls import patterns, url, include
from django.conf.urls.i18n import i18n_patterns

from app import views
from app.views import api

urlpatterns = patterns('',
    url(r'^userpic', api.GetUserpic.as_view(), name='api_userpic'),
    url(r'^song_url', api.GetSongUrl.as_view(), name='api_song_url'),
    url(r'^rate', api.Rate.as_view(), name='api_rate'),
    url(r'^characterise', api.ListenCharacterise.as_view(), name='api_characterise'),
    url(r'^recommend', api.Recommend.as_view(), name='api_recommend'),
)