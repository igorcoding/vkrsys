from social_auth.db.django_models import UserSocialAuth


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


class MQ:
    def __init__(self):
        pass

