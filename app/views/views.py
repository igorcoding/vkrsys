import uuid
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.defaults import page_not_found
from django.views.generic import View
from django.contrib.auth import logout
from django.utils.translation import ugettext as _

from app import tasks
from app.views.basicscripts import VkSocial, Db, force_logout_wrapper


class MyView(View):
    initial_params = {
        'title': 'VK Recommender'
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
    template = 'login.html'

    def get(self, request):
        if request.user.is_authenticated():
            return redirect(reverse('app:home'))

        params = self.build_params({
            'title': MyView.initial_params['title'] + '. ' + _('Login'),
            'text': request.user.is_authenticated(),
            'login_btn_text': _('Sign in with VK'),
            'login_btn_url': settings.VK_LOGIN_URL
        })

        return self._render(request, self.template, params)

    def post(self, request):
        params = self.build_params()
        return self._render(request, self.template, params)


class HomePageView(MyView):
    template = 'home.html'

    @method_decorator(login_required)
    @method_decorator(force_logout_wrapper)
    def get(self, request, username):
        target_username = username
        if target_username is None:
            target_username = request.user.username

        try:
            User.objects.get(username=target_username)
        except ObjectDoesNotExist:
            return page_not_found(request)

        user_id = request.user.id
        access_token, user_vk_id = VkSocial.get_access_token_and_id(request)

        params = {
            'username': request.user.username,
            'name': "%s %s" % (request.user.first_name, request.user.last_name),
            'user_vk_url': 'https://vk.com/id' + user_vk_id,
            'target_username': target_username
        }

        user_uuid = uuid.uuid4()
        request.session['uuid'] = str(user_uuid)
        response = self._render(request, self.template, params)
        response.set_cookie(key='uuid', value=user_uuid)
        tasks.save_music.delay(user_vk_id, access_token)
        return response


class AboutView(MyView):
    template = 'about.html'

    @method_decorator(login_required)
    @method_decorator(force_logout_wrapper)
    def get(self, request):
        user_id = request.user.id
        access_token, user_vk_id = VkSocial.get_access_token_and_id(request)

        params = {
            'username': "%s %s" % (request.user.first_name, request.user.last_name),
            'user_vk_url': 'https://vk.com/id' + user_vk_id,
            'login_btn_text': _('Proceed'),
            'login_btn_url': reverse('app:home')
        }
        return self._render(request, self.template, params)


def music_fetch(request):
    user_id = request.user.id
    access_token, user_vk_id = VkSocial.get_access_token_and_id(request)
    res = tasks.save_music.delay(user_vk_id, access_token)
    # pprint(res.get())
    return HttpResponse("getting music...")


class LogoutView(MyView):
    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
        return redirect(reverse('app:login'))
