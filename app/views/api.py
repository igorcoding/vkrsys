import json
from django.conf import settings
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.generic import View
from requests import ConnectionError
from requests.exceptions import ReadTimeout

from app.views.basicscripts import Db, VkSocial
from app.views.status import STATUS, MSG, REDIRECT_RESPONSE


def ensure_present(required, attr_name='GET'):
    def real_wrapper(f):
        def wrapper(*args, **kwargs):
            d = getattr(args[0], attr_name)
            if attr_name not in ['GET', 'POST']:
                d = json.loads(d, encoding='utf-8')
                args += (d, )
            absent = []
            for arg in required:
                if arg not in d:
                    absent.append(arg)

            if len(absent) > 0:
                return JsonResponse({
                    'status': STATUS['absent'],
                    'reason': MSG['absent'],
                    'absent': absent
                }, status=STATUS['absent'])
            else:
                return f(*args, **kwargs)
        return wrapper
    return real_wrapper


class GetUserpic(View):

    @method_decorator(login_required)
    def get(self, request):
        access_token, user_vk_id = VkSocial.get_access_token_and_id(request)
        status, userpic = VkSocial.get_userpic(user_vk_id, access_token)
        if status == STATUS['unauthorized']:
            return JsonResponse(REDIRECT_RESPONSE)

        if status == STATUS['ok']:
            return JsonResponse({
                'status': status,
                'msg': MSG['ok'],
                'url': userpic
            })


class GetSongUrl(View):
    PARAMS = ['song_id']

    @method_decorator(login_required)
    @method_decorator(ensure_present(PARAMS))
    def get(self, request):
        access_token, vk_uid = VkSocial.get_access_token_and_id(request)
        try:
            song_id = request.GET['song_id']
            status, url = VkSocial.get_song_url(vk_uid, song_id, access_token)
            if status == STATUS['ok']:
                return JsonResponse({
                    'status': status,
                    'url': url
                }, status=status)
            if status == STATUS['unauthorized']:
                return JsonResponse(REDIRECT_RESPONSE)
        except (ConnectionError, ReadTimeout):
            return JsonResponse({
                'status': 500,
                'reason': 'Connection Error'
            }, status=500)
        except ObjectDoesNotExist:
            return JsonResponse({
                'status': 404,
                'reason': 'song not found'
            }, status=404)


class Recommend(View):
    PARAMS = ['limit', 'offset']
    INITIAL_TEMPLATE_NAME = 'player.html'
    PLAYLIST_ENTRIES_TEMPLATE_NAME = 'playlist_entries.html'

    @method_decorator(login_required)
    @method_decorator(ensure_present(PARAMS))
    def get(self, request):
        user_id = request.user.id
        d = request.GET

        try:
            limit = int(d['limit'])
            offset = int(d['offset'])
            initial = bool(int(d['initial'])) if 'initial' in d else False
            with_content = bool(int(d['with_content'])) if 'with_content' in d else initial
        except ValueError:
            return JsonResponse({
                'status': 400,
                'reason': 'Malformed request'
            }, status=400)
        templ = self.INITIAL_TEMPLATE_NAME if initial and with_content else self.PLAYLIST_ENTRIES_TEMPLATE_NAME
        recs = Db.get_recommendations(user_id, limit=limit, offset=offset, initial=initial)

        if recs is not None:
            return JsonResponse({
                'status': 200,
                'count': len(recs),
                'result': render_to_string(templ, dict(recs=recs))
            })
        else:
            return JsonResponse({
                'status': 500
            }, status=500)


class ListenCharacterise(View):
    PARAMS = ['song_id', 'hops_count', 'duration']

    @method_decorator(login_required)
    @method_decorator(ensure_present(PARAMS, 'body'))
    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        uuid = request.COOKIES.get('uuid')
        if uuid is None or 'uuid' not in request.session or uuid != request.session['uuid']:
            return redirect('/')

        try:
            rating_obj = Db.listen_characterise(uuid, user_id, args[0])
            if rating_obj is None:
                return JsonResponse({
                    'status': 201,
                    'msg': 'Something is wrong'
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

        pass


class Rate(View):
    PARAMS = ['song_id', 'direction']
    ACTION_TYPE = 'rate'

    @method_decorator(login_required)
    @method_decorator(ensure_present(PARAMS, 'body'))
    def post(self, request, *args):
        user_id = request.user.id
        d = args[0]

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
                'status': 200,
                'msg': 'Vote accepted'
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


