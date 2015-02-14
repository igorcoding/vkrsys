from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
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
        return absent
    return None


class GetSongUrl(View):
    PARAMS = ['song_id']

    @method_decorator(login_required)
    def get(self, request):
        user_id = request.user.id
        d = request.GET
        absent = ensure_present(d, self.PARAMS)
        if absent:
            return JsonResponse({
                'status': 400,
                'reason': 'required params are not present',
                'absent': absent
            }, status=400)

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
            return JsonResponse({
                'status': 400,
                'reason': 'required params are not present',
                'absent': absent
            }, status=400)

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
                    'status': 400,
                    'msg': 'You have already rated this song'
                }, status=400)

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


