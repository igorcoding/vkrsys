from pprint import pprint


def user_created(backend, details, user=None, is_new=False, *args, **kwargs):
    if user is not None and is_new:
        pprint(user)
        # return user