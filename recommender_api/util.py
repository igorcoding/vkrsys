from recommender_api.response import Responses, RespError


def ok_on_success(f):
    def wrapper(self, *args, **kwargs):
        ret = f(self, *args, **kwargs)
        if ret is None:
            return Responses.OK
        else:
            return ret

    return wrapper


def model_initialized_required(f):
    def wrapper(self, *args, **kwargs):
        if self.initialized and self.svd is not None:
            return f(self, *args, **kwargs)
        else:
            raise RespError(Responses.MODEL_NOT_INITIALIZED)

    return wrapper