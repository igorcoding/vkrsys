from pprint import pprint
from app import tasks
from app.views import VkSocial
from recommender_api.rsys_actions import RsysActions


def user_created(backend, details, user=None, is_new=False, *args, **kwargs):
    if user is not None and is_new:
        data = {
            'user_id': user.id
        }
        access_token, vk_uid = VkSocial.get_access_token_and_id_by_uid(user.id)
        print access_token, vk_uid
        tasks.api_request.delay(RsysActions.USERS_ADD, data)