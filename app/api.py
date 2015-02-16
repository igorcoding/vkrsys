from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic import View
from app import tasks
from app.basicscripts import Db, VkSocial


def ensure_present(d, args):
    absent = []
    for arg in args:
        if arg not in d:
            absent.append(arg)

    if len(absent) > 0:
        return JsonResponse({
                                'status': 400,
                                'reason': 'required params are not present',
                                'absent': absent
                            }, status=400)
    return None


class GetUserpic(View):
    STATUS = {
        'ok': 200,
        'token_expired': 501,
        'unknown': 500
    }

    MSG = {
        200: 'ok',
        501: 'token expired',
        500: 'unknown'
    }

    def _get_userpic(self, user_id, user_vk_id, access_token):
        cache_key = 'userpic_%s' % user_vk_id
        userpic = cache.get(cache_key)
        status = 200
        if userpic is None:
            try:
                userpic_res = tasks.fetch_userpic.delay(user_id, user_vk_id, access_token)
                userpic = userpic_res.get()
                cache.set(cache_key, userpic, 60 * 30)
                if userpic is None:
                    status = self.STATUS['token_expired']
            except:
                status = self.STATUS['unknown']
        return status, userpic

    @method_decorator(login_required)
    def get(self, request):
        user_id = request.user.id
        access_token, user_vk_id = VkSocial.get_access_token_and_id(request)
        status, userpic = self._get_userpic(user_id, user_vk_id, access_token)

        return JsonResponse({
            'status': status,
            'msg': self.MSG[status],
            'url': userpic
        })


class GetSongUrl(View):
    PARAMS = ['song_id']

    @method_decorator(login_required)
    def get(self, request):
        user_id = request.user.id
        d = request.GET
        absent = ensure_present(d, self.PARAMS)
        if absent:
            return absent

        access_token, user_vk_id = VkSocial.get_access_token_and_id(request)
        try:
            url = tasks.fetch_song_url(d['song_id'], user_vk_id, access_token)
            return JsonResponse({
                                    'status': 200,
                                    'url': url
                                }, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({
                                    'status': 404,
                                    'reason': 'song not found'
                                }, status=404)


class Recommend(View):
    PARAMS = ['limit', 'offset']
    INITIAL_TEMPLATE_NAME = 'main_content.html'
    PLAYLIST_ENTRIES_TEMPLATE_NAME = 'playlist_entries.html'

    @method_decorator(login_required)
    def get(self, request):
        user_id = request.user.id
        d = request.GET
        absent = ensure_present(d, self.PARAMS)
        if absent:
            return absent

        try:
            limit = int(d['limit'])
            offset = int(d['offset'])
            initial = bool(int(d['initial'])) if 'initial' in d else False
        except ValueError:
            return JsonResponse({
                'status': 400,
                'reason': 'Malformed request'
            }, status=400)

        recs = Db.get_recommendations(user_id, limit=limit, offset=offset)

        templ = self.INITIAL_TEMPLATE_NAME if initial else self.PLAYLIST_ENTRIES_TEMPLATE_NAME

        return JsonResponse({
            'status': 200,
            'count': len(recs),
            'result': render_to_string(templ, dict(recs=recs))
        })


class Rate(View):
    PARAMS = ['song_id', 'direction']
    ACTION_TYPE = 'rate'

    @method_decorator(login_required)
    def get(self, request):
        # TODO: move to POST probably

        user_id = request.user.id

        d = request.GET
        absent = ensure_present(d, self.PARAMS)
        if absent:
            return absent

        try:
            song_id = int(d['song_id'])
        except ValueError:
            return JsonResponse({
                                    'status': 400,
                                    'reason': 'song_id is not numeric'
                                }, status=400)

        try:
            rating_obj = Db.rate(user_id, song_id, d['direction'])
            if rating_obj is None:
                return JsonResponse({
                                        'status': 201,
                                        'msg': 'You have already rated this song'
                                    }, status=200)

            return JsonResponse({
                                    'status': 200
                                }, status=200)

        except ObjectDoesNotExist as e:
            return JsonResponse({
                                    'status': 404,
                                    'reason': 'unknown entry',
                                    'msg': e.message
                                }, status=404)
        except Exception as e:
            return JsonResponse({
                                    'status': 500,
                                    'reason': 'unknown error. ' + str(e.__class__),
                                    'msg': e.message
                                }, status=500)

    @method_decorator(login_required)
    def post(self, request):
        return JsonResponse({
                                'status': 405
                            }, status=405)


