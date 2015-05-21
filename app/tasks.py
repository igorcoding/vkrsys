from __future__ import absolute_import
from contextlib import closing
import json
import os
from pprint import pprint
from urllib3.exceptions import TimeoutError
import urlparse

from dejavu import Dejavu

from dejavu.recognize import FileRecognizer
from celery import shared_task
from requests.exceptions import ReadTimeout
import vk
from vk.api import VkAPIMethodError, VkError
import requests
from django.conf import settings
from django.core.cache import cache

from app.models import Song
from mutagen import File


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
def api_request(action, data):
    url = settings.API_URL + action
    resp = requests.post(url, json=data)
    jresp = json.loads(resp.text, encoding='utf-8')
    return jresp


@shared_task
def fetch_friends_music(user_id, vk_uid, access_token):
    vkapi = vk.API(access_token=access_token)

    pass


@shared_task
def save_music(vk_uid, access_token):
    vkapi = vk.API(access_token=access_token)
    try:
        songs = vkapi.audio.get(owner_id=vk_uid, need_user=0)
    except VkError as e:
        return "vk error: %s" % e.message
    except ReadTimeout:
        songs = {
            'items': []
        }

    last_song = Song.objects.order_by('id').last()
    if last_song is None:
        p_last_id = 0
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

    key = "p_last_song_id"
    if cache.get(key) is None:
        cache.set(key, p_last_id, None)


@shared_task
def download_and_process_songs(limit):
    p_last_id = cache.get("p_last_song_id")
    if p_last_id is None:
        print 'no songs to process'
        return  # no need in downloading - everything is already processed
    else:
        cache.delete("p_last_song_id")
    songs = Song.objects.filter(id__gt=p_last_id)
    print 'Started download_and_process_songs'
    exec_songs = songs if limit is None else songs[:limit]
    for s in exec_songs:
        download_and_process_song.delay(dict(id=s.id, url=s.url))


@shared_task
def download_and_process_song(s):
    s_id = s['id']
    s_url = s['url']
    song = Song.objects.get(pk=s_id)
    song_path = os.path.join(settings.SONGS_PATH, '%d.mp3' % s_id)
    if type(s_url) == unicode and not os.path.exists(song_path):
        try:
            r = requests.get(s_url)
            with closing(open(song_path, 'wb')) as f:
                f.write(r.content)
        except ReadTimeout:
            print 'No Connection'

    if _process_song(song_path, s) is None:
        art_path = os.path.join(settings.SONGS_ARTS_PATH, '%d.png' % s_id)
        if os.path.exists(song_path):
            if not os.path.exists(art_path):
                f = File(song_path)
                if f and 'APIC:' in f.tags:
                    artwork = f.tags['APIC:'].data
                    with closing(open(art_path, 'wb')) as img:
                        img.write(artwork)
                    song.art_url = urlparse.urljoin(settings.SONGS_ARTS_URL, '%d.png' % s_id)
                    song.save()
            fingerprint_song.delay(song_path)
            return '+ %s' % str(s_id)
    return '- %s' % str(s_id)


def _process_song(filename, song):
    threshold = 1000
    limit = 6  # seconds
    f = djv.recognize(FileRecognizer, filename, limit)
    if f is None or f['confidence'] < threshold:
        return None
    else:
        print "Recognized: %s" % str(f)
        song.delete()

    return filename


@shared_task(ignore_result=True)
def fingerprint_song(filename):
    return
    djv.fingerprint_file(filename, id_in_filename=True)


@shared_task
def rsys_learn_online():
    result = api_request('learn_online', {})


@shared_task
def rsys_learn_offline():
    result = api_request('learn_offline', {})