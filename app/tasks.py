from __future__ import absolute_import

from celery import shared_task
from django.contrib.auth.models import User
import vk
from app.models import Song


@shared_task
def fetch_userpic(user_id, vk_uid, access_token):
    vkapi = vk.API(access_token=access_token)
    user_info = vkapi.users.get(user_ids=vk_uid, fields=['photo_50'])[0]
    return user_info['photo_50']


@shared_task
def fetch_music(vk_uid, access_token):
    vkapi = vk.API(access_token=access_token)
    songs = vkapi.audio.get(owner_id=vk_uid, need_user=0)

    batch_limit = 500

    bulk = []
    for s in songs['items']:
        song = Song(
            owner_id=s['owner_id'],
            song_id=s['id'],
            artist=s['artist'],
            title=s['title'],
            duration=s['duration'],
            url=s['url'])
        if 'genre_id' in s:
            song.genre = s['genre_id']

        bulk.append(song)
        if len(bulk) >= batch_limit:
            Song.objects.bulk_create_new(bulk)
            bulk = []

    if len(bulk) != 0:
        Song.objects.bulk_create_new(bulk)

    return songs
