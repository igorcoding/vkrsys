from __future__ import absolute_import

from celery import shared_task
import vk
from app.models import Song


@shared_task
def fetch_music(vk_uid, access_token):
    vkapi = vk.API(access_token=access_token)
    songs = vkapi.audio.get(owner_id=vk_uid, need_user=0)

    batch_limit = 500

    bulk = []  # TODO: bulk save without Integrity checks
    for s in songs['items']:
        song = Song(
            s_id=s['id'],
            artist=s['artist'],
            title=s['title'],
            duration=s['duration'],
            url=s['url'])
        if 'genre' in s:
            song.genre = s['genre']

        bulk.append(song)
        if len(bulk) >= batch_limit:
            Song.objects.bulk_create_new(bulk)
            bulk = []

    if len(bulk) != 0:
        Song.objects.bulk_create_new(bulk)

    return songs
