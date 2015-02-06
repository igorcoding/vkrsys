from pprint import pprint
from app import tasks
from recommender_api.rsys_actions import RsysActions


def user_created(backend, details, user=None, is_new=False, *args, **kwargs):
    if user is not None and is_new:
        data = {
            'user_id': user.id
        }
        # tasks.api_request.delay(RsysActions.USERS_ADD, data)