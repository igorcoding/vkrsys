import json
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError, connection
from social_auth.db.django_models import UserSocialAuth
from app import tasks
from app.models import Rating, Song, UserAction
from django.core.exceptions import ObjectDoesNotExist
from recommender_api.rsys_actions import RsysActions



class VkSocial:
    VK_PROVIDER = 'vk-oauth'

    def __init__(self):
        raise Exception("Abstract class")

    @staticmethod
    def get_access_token_and_id(request):
        if request.user.is_authenticated():
            instance = UserSocialAuth.objects.filter(provider=VkSocial.VK_PROVIDER).get(user_id=request.user.id)
            access_token = instance.tokens['access_token']
            user_vk_id = instance.uid
            return access_token, user_vk_id
        return None

    @staticmethod
    def get_userpic(user_id, user_vk_id, access_token):
        cache_key = 'userpic_%s' % user_vk_id
        userpic = cache.get(cache_key)
        if userpic is None:
            userpic_res = tasks.fetch_userpic.delay(user_id, user_vk_id, access_token)
            userpic = userpic_res.get()
            cache.set(cache_key, userpic, 60 * 30)
        return userpic


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

        rating = -1
        if direction == 'up':
            rating = 1
        elif direction == 'down':
            rating = 0
        else:
            raise AttributeError("Unknown direction: %s" % direction)

        rating_obj = Rating(user=user, song=song, rating=rating)

        try:
            rating_obj.save()
        except IntegrityError:
            return None

        Db.transact(user_id, song_id, RsysActions.RATE, {
            'user_id': user_id,
            'item_id': song_id,
            'direction': direction,
            'rating': rating_obj.rating
        })
        return rating_obj

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
    def get_recommendations(user_id, refresh=True, limit=30, offset=0):
        api_resp = tasks.api_request('recommend', {
            'user_id': user_id,
            'refresh': refresh
        })

        if not api_resp or api_resp['code'] != 200 and api_resp['code'] != 201:
            return None

        q = """select app_song.song_id, app_song.artist, app_song.title, app_song.duration, app_song.genre  from recs join
               app_song on app_song.id = recs.song_id where user_id = %s
               ORDER BY score desc limit %s offset %s""" % (user_id, limit, offset)

        recs = Db._custom_raw_sql(q)
        return recs

