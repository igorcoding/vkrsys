from pprint import pprint
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.auth import logout
from social_auth.db.django_models import UserSocialAuth
import vk
from app import tasks


class MyView(View):
    initial_params = {
        'title': 'VK Music Recommender'
    }

    def build_params(self, d=None):
        params = self.initial_params
        if d is not None:
            return dict(params, **d)
        return params

    @staticmethod
    def _render(request, template, params=initial_params, **kwargs):
        return render(request, template, params, **kwargs)


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
        instance = UserSocialAuth.objects.filter(provider='vk-oauth').get(user_id=user_id)
        access_token = instance.tokens['access_token']
        user_vk_id = instance.uid
        print access_token

        res = tasks.fetch_music.delay(user_vk_id, access_token)
        pprint(res.get())

        return self._render(request, self.template)


class LogoutView(MyView):

    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
        return redirect('/login')