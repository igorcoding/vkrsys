from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
from app.basicscripts import Db


def ensure_present(d, args):
    absent = []
    for arg in args:
        if arg not in d:
            absent.append(arg)

    if len(absent) > 0:
        return absent
    return None


class GetSongUrl(View):
    PARAMS = ['song_id', 'direction']

    @method_decorator(login_required)
    def get(self, request):
        user_id = request.user.id

        pass


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
                'reason': 'unknown error',
                'msg': e.message
            }, status=500)

    @method_decorator(login_required)
    def post(self, request):
        return JsonResponse({
            'status': 405
        }, status=405)


