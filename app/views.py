from pprint import pprint
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.auth import logout
from social_auth.db.django_models import UserSocialAuth
import vk
from app import tasks
from app.basicscripts import VkSocial, Rsys


class MyView(View):
    initial_params = {
        'title': 'VK Music Recommender'
    }

    def build_params(self, d=None):
        params = self.initial_params
        if d is not None:
            return dict(params, **d)
        return params

    def _render(self, request, template, params=None, **kwargs):
        p = self.build_params(params)
        return render(request, template, p, **kwargs)


class LoginView(MyView):
    initial_params = {
        'title': MyView.initial_params['title'] + '. Login'
    }

    template = 'login.html'

    def get(self, request):
        if request.user.is_authenticated():
            return redirect('/')

        params = self.build_params({
            'text': request.user.is_authenticated()
        })
        return self._render(request, self.template, params)

    def post(self, request):
        params = self.build_params()
        return self._render(request, self.template, params)


class HomePageView(MyView):
    template = 'index.html'

    @method_decorator(login_required)
    def get(self, request):
        user_id = request.user.id
        access_token, user_vk_id = VkSocial.get_access_token_and_id(request)
        userpic = VkSocial.get_userpic(user_id, user_vk_id, access_token)
        # res = tasks.fetch_music.delay(user_vk_id, access_token)
        # pprint(res.get())

        params = {
            'username': "%s %s" % (request.user.first_name, request.user.last_name),
            'userpic': userpic
        }

        return self._render(request, self.template, params)


class LogoutView(MyView):

    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
        return redirect('/login')


class Api:
    def __init__(self):
        pass

    @staticmethod
    def ensure_present(d, args):
        absent = []
        for arg in args:
            if arg not in d:
                absent.append(arg)

        if len(absent) > 0:
            return absent
        return None

    class Rate(View):
        PARAMS = ['user_id', 'song_id', 'rating']

        @method_decorator(login_required)
        def get(self, request):
            # TODO: move to POST probably

            d = request.GET
            absent = Api.ensure_present(d, self.PARAMS)
            if absent:
                return JsonResponse({
                    'status': 400,
                    'reason': 'required params are not present',
                    'absent': absent
                }, status=400)

            try:
                Rsys.rate(int(d['user_id']), int(d['song_id']), float(d['rating']))
            except ValueError:
                return JsonResponse({
                    'status': 400,
                    'reason': 'some params are not numeric'
                }, status=400)

            return JsonResponse({
                'status': 200
            }, status=200)

        @method_decorator(login_required)
        def post(self, request):
            return JsonResponse({
                'status': 405
            }, status=405)








