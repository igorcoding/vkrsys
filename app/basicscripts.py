from django.core.cache import cache
from social_auth.db.django_models import UserSocialAuth
from app import tasks


class VkSocial:
    VK_PROVIDER = 'vk-oauth'

    def __init__(self):
        pass

    @staticmethod
    def get_access_token_and_id(request):
        if request.user.is_authenticated():
            instance = UserSocialAuth.objects.filter(provider=VkSocial.VK_PROVIDER).get(user_id=request.user.id)
            access_token = instance.tokens['access_token']
            user_vk_id = instance.uid
            return access_token, user_vk_id
        return None

    @staticmethod
    def get_userpic(user_id, user_vk_id, access_token):
        cache_key = 'userpic_%s' % user_vk_id
        userpic = cache.get(cache_key)
        if userpic is None:
            userpic_res = tasks.fetch_userpic.delay(user_id, user_vk_id, access_token)
            userpic = userpic_res.get()
            cache.set(cache_key, userpic, 60*30)
        return userpic


class MQ:
    def __init__(self):
        pass


class Rsys:
    def __init__(self):
        pass

