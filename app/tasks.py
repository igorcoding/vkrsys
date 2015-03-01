from __future__ import absolute_import
from contextlib import closing
import json
import os
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
from pprint import pprint

from celery import shared_task
from django.contrib.auth.models import User
import vk
from vk.api import VkAPIMethodError
from app.models import Song
import requests

from django.conf import settings


def catcher(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return None
    return wrapper


db = settings.DATABASES['default']
config = {
    "database": {
        "host": db['HOST'],
        "user": db['USER'],
        "passwd": db['PASSWORD'],
        "db": db['NAME'],
    }
}

djv = Dejavu(config)


@shared_task
# @catcher
def fetch_song_url(song_id, vk_uid, access_token):
    s = Song.objects.get(pk=song_id)
    vk_song_id = '%d_%d' % (s.owner_id, s.song_id)

    vkapi = vk.API(access_token=access_token)
    try:
        audio_info = vkapi.audio.getById(audios=vk_song_id)
        s.url = audio_info[0]['url']
        s.save()
        return s.url
    except VkAPIMethodError as e:
        pprint(e.message)



@shared_task
# @catcher
def fetch_userpic(user_id, vk_uid, access_token):
    try:
        vkapi = vk.API(access_token=access_token)
        user_info = vkapi.users.get(user_ids=vk_uid, fields=['photo_50'])[0]
        return user_info['photo_50']
    except VkAPIMethodError:
        return None


@shared_task
# @catcher
def fetch_music(vk_uid, access_token):
    vkapi = vk.API(access_token=access_token)
    songs = vkapi.audio.get(owner_id=vk_uid, need_user=0)

    last_song = Song.objects.order_by('id').last()
    if last_song is None:
        p_last_id = -1
    else:
        p_last_id = last_song.id

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

    new_songs = Song.objects.filter(id__gt=p_last_id)
    # download_and_process_songs.delay(map(lambda s1: (s1.id, s1.url), new_songs))


@shared_task
def api_request(action, data):
    url = settings.API_URL + action
    resp = requests.post(url, json=data)
    jresp = json.loads(resp.text, encoding='utf-8')
    return jresp


@shared_task
def download_and_process_songs(songs):
    for s in songs[0:4]:
        r = requests.get(s[1])
        filename = '/home/igor/Projects/python/vkrsys/songs/%s' % str(s[0])
        with closing(open(filename, 'wb')) as f:
            f.write(r.content)

        _process_song(filename, s[0])


@shared_task
def _process_song(filename, song_id):
    f = djv.recognize(FileRecognizer, filename)
    if f is None:
        djv.fingerprint_file(filename)
    else:
        print "Recognized: %s" % str(f)

    s = Song.objects.get(id=song_id)
    s.url = None
    s.save()

    os.remove(filename)
    return filename


@shared_task
def rsys_learn_online():
    result = api_request('learn_online', {})


@shared_task
def rsys_learn_offline():
    result = api_request('learn_offline', {})