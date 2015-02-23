from response import Responses, RespError, R


def ok_on_success(f):
    def wrapper(self, *args, **kwargs):
        ret = f(self, *args, **kwargs)
        if ret is None or ret is True:
            return R(Responses.OK)
        elif not ret:
            return R(Responses.NOT_OK)
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


def generate(what, n):
    for i in xrange(n):
        yield what