import uuid

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.auth import logout

from app import tasks
from app.views.basicscripts import VkSocial, Db


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

        params = {
            'username': "%s %s" % (request.user.first_name, request.user.last_name),
            'user_vk_url': 'https://vk.com/id' + user_vk_id,
        }

        user_uuid = uuid.uuid4()
        request.session['uuid'] = str(user_uuid)
        response = self._render(request, self.template, params)
        response.set_cookie(key='uuid', value=user_uuid)
        return response


def music_fetch(request):
    user_id = request.user.id
    access_token, user_vk_id = VkSocial.get_access_token_and_id(request)
    res = tasks.fetch_music.delay(user_vk_id, access_token)
    # pprint(res.get())
    return HttpResponse("getting music...")


class LogoutView(MyView):

    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
        return redirect('/login')
