from __future__ import absolute_import
from pprint import pprint

from celery import shared_task
from django.contrib.auth.models import User
import vk
import rsys
from app.models import Song


@shared_task
def r():
    m = rsys.data_sources.matrix(4, 4)
    m.set(0, 0, 4)
    m.set(0, 1, 5)
    m.set(0, 2, 2)
    m.set(0, 3, -1)

    m.set(1, 0, -1)
    m.set(1, 1, 4)
    m.set(1, 2, 4)
    m.set(1, 3, 3)

    m.set(2, 0, -1)
    m.set(2, 1, 2)
    m.set(2, 2, -1)
    m.set(2, 3, -1)

    m.set(3, 0, 5)
    m.set(3, 1, 4)
    m.set(3, 2, -1)
    m.set(3, 3, -1)

    config = rsys.SVDConfig(m, 4, 0.05)

    svd = rsys.SVD(config)
    # svd.learn()

    # for i in xrange(0, m.rows):
    #     for j in xrange(0, m.cols):
    #         print "%d " % m.at(i, j),
    #     print
    # print
    #
    # for i in xrange(0, m.rows):
    #     for j in xrange(0, m.cols):
    #         print "%f " % svd.predict(i, j),
    #     print
    pass

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
