import json
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError, connection
from social_auth.db.django_models import UserSocialAuth
import vk
from vk.api import VkAPIMethodError
from app import tasks
from app.models import Rating, Song, UserAction, ListenCharacteristic
from django.core.exceptions import ObjectDoesNotExist
from app.views.status import STATUS
from recommender_api.rsys_actions import RsysActions


class VkSocial:
    VK_PROVIDER = 'vk-oauth'

    def __init__(self):
        raise Exception("Abstract class")

    @classmethod
    def get_access_token_and_id(cls, request):
        if request.user.is_authenticated():
            return cls.get_access_token_and_id_by_uid(request.user.id)
        return None

    @classmethod
    def get_access_token_and_id_by_uid(cls, uid):
        instance = UserSocialAuth.objects.filter(provider=cls.VK_PROVIDER).get(user_id=uid)
        access_token = instance.tokens['access_token']
        user_vk_id = instance.uid
        return access_token, user_vk_id

    @classmethod
    def _fetch_userpic(cls, vk_uid, access_token):
        try:
            vkapi = vk.API(access_token=access_token)
            user_info = vkapi.users.get(user_ids=vk_uid, fields=['photo_50'])[0]
            return STATUS['ok'], user_info['photo_50']
        except VkAPIMethodError:
            return STATUS['unauthorized'], None

    @classmethod
    def get_userpic(cls, vk_uid, access_token):
        status = STATUS['ok']
        cache_key = 'userpic__%s' % vk_uid
        userpic = cache.get(cache_key)
        if userpic is None:
            try:
                status, userpic = cls._fetch_userpic(vk_uid, access_token)
                if userpic is not None:
                    cache.set(cache_key, userpic, settings.USERPIC_CACHE_DURATION)
            except:
                status = STATUS['unknown']
        return status, userpic

    @classmethod
    def _fetch_song_url(cls, song_id, access_token):
        s = Song.objects.get(pk=song_id)
        vk_song_id = '%d_%d' % (s.owner_id, s.song_id)

        vkapi = vk.API(access_token=access_token)
        try:
            audio_info = vkapi.audio.getById(audios=vk_song_id)
            s.url = audio_info[0]['url']
            s.save()
            return STATUS['ok'], s.url
        except VkAPIMethodError as e:
            return STATUS['unauthorized'], None

    @classmethod
    def get_song_url(cls, vk_uid, song_id, access_token):
        status = STATUS['ok']
        cache_key = 'songurl__%s__%s' % (vk_uid, song_id)
        song_url = cache.get(cache_key)
        if song_url is None:
            try:
                status, song_url = cls._fetch_song_url(song_id, access_token)
                if song_url is not None:
                    cache.set(cache_key, song_url, settings.SONG_URL_CACHE)
            except:
                status = STATUS['unknown']
        return status, song_url


class Db:
    MAX_VOTES = 1

    UPVOTE_W = 0.4
    DOWNVOTE_W = 0.6
    RATING_MAX = 5
    MAX_SCORE = (MAX_VOTES + 0.5) / 0.5

    def __init__(self):
        raise Exception("Abstract class")

    @staticmethod
    def compute_total_rating(rating_obj):
        """
            Computes total rating based on user activity
        :param rating_obj: Rating
        :return: total rating
        :rtype: float
        """
        relative_score = (rating_obj.up_votes + 0.5) / (rating_obj.down_votes + 0.5)
        return relative_score / Db.MAX_SCORE * Db.RATING_MAX

    @staticmethod
    def rate(user_id, song_id, direction):
        user = User.objects.get(pk=user_id)
        song = Song.objects.get(pk=song_id)

        if direction == 'up':
            rating = 1
        elif direction == 'down':
            rating = 0
        else:
            raise AttributeError("Unknown direction: %s" % direction)

        try:
            rating_obj = Rating.objects.get(user=user, song=song)
            if not rating_obj.is_implicit:
                return None
        except ObjectDoesNotExist:
            rating_obj = Rating(user=user, song=song)

        rating_obj.rating = rating
        rating_obj.is_implicit = False

        try:
            rating_obj.save()
        except IntegrityError:
            return None

        Db.transact(user_id, song_id, 'rate', {
            'user_id': user_id,
            'item_id': song_id,
            'direction': direction,
            'rating': rating_obj.rating
        })
        return rating_obj

    @staticmethod
    def listen_characterise(uuid, user_id, payload):
        song_id = payload['song_id']
        hops_count = payload['hops_count']
        duration = payload['duration']

        if duration < 0:
            print 'Duration < 0'
            return

        user = User.objects.get(pk=user_id)
        song = Song.objects.get(pk=song_id)

        try:
            o = ListenCharacteristic.objects.get(uuid=uuid, user=user, song=song)
        except ObjectDoesNotExist:
            o = ListenCharacteristic(uuid=uuid, user=user, song=song)

        o.user = user
        o.song = song
        o.hops_count = hops_count
        o.listen_duration = duration

        try:
            o.save()
        except IntegrityError:
            return None

        avg_duration = 0.0
        characters = ListenCharacteristic.objects.filter(user=user, song=song)
        for ch in characters:
            avg_duration += ch.listen_duration
        avg_duration /= len(characters)

        try:
            rate_o = Rating.objects.get(user=user, song=song)
            is_new = False
        except ObjectDoesNotExist:
            rate_o = Rating(user=user, song=song)
            is_new = True

        if is_new or rate_o.is_implicit:
            rate_o.is_implicit = True
            rate_o.rating = avg_duration / float(song.duration)

            rate_o.save()

        Db.transact(user_id, song_id, 'characterise', {
            'user_id': user_id,
            'item_id': song_id,
            'hops_count': hops_count,
            'duration': duration
        })

        return o

    @staticmethod
    def transact(user_id, song_id, action_type, activity):
        action = UserAction(user=User.objects.get(pk=user_id),
                            song=Song.objects.get(pk=song_id),
                            action_type=action_type,
                            action_json=json.dumps(activity, ensure_ascii=False))

        action.save()

    @staticmethod
    def _custom_raw_sql(q, params=list()):
        with connection.cursor() as c:
            c.execute(q, list(params))
            return c.fetchall()

    @staticmethod
    def get_recommendations(user_id, limit=30, offset=0, refresh=True, initial=False):
        if initial:
            api_resp = tasks.api_request('recommend', {
                'user_id': user_id,
                'refresh': refresh
            })

            if not api_resp or (api_resp['code'] != 200 and api_resp['code'] != 201):
                return None

        q = """select app_song.id, app_song.artist, app_song.title, app_song.duration, app_song.genre, app_song.art_url, app_rating.rating
                from recs join app_song on app_song.id = recs.song_id
                  left join app_rating on app_song.id = app_rating.song_id and app_rating.user_id = recs.user_id
                where recs.user_id = %s
                order by score desc limit %s offset %s""" % (user_id, limit, offset)

        recs = Db._custom_raw_sql(q)
        return recs

