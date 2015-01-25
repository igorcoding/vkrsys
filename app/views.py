from pprint import pprint
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
        instance = UserSocialAuth.objects.filter(provider='vk-oauth').get(user_id=user_id)
        instance.refresh_token()
        access_token = instance.tokens['access_token']
        user_vk_id = instance.uid
        print access_token

        userpic_res = tasks.fetch_userpic.delay(request.user.id, user_vk_id, access_token)
        userpic = userpic_res.get()
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