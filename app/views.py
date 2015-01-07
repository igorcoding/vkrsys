from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.auth import logout
from social_auth.db.django_models import UserSocialAuth
import vk


class MyView(View):
    initial_params = {
        'title': 'VK Rsys.'
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
        'title': 'VK Rsys. Login.'
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

        vkapi = vk.API(access_token=access_token)
        music = vkapi.audio.get(owner_id=user_vk_id, need_user=0, count=3)
        print music

        return self._render(request, self.template)


class LogoutView(MyView):

    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
        return redirect('/login')