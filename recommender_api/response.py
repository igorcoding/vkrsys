import copy


class ResponseResult:
    def __init__(self, code, status, msg, data=None):
        self.code = code
        self.status = status
        self.msg = msg
        self.extra_msg = None
        self.data = data

    def to_res(self):
        d = {
            'code': self.code,
            'msg': self.msg
        }
        if self.data is not None:
            d['data'] = self.data
        if self.extra_msg is not None:
            d['exra_msg'] = self.extra_msg
        return self.status, d

    def d(self, data):
        self.data = data
        return self

    def m(self, extra_msg):
        self.msg += extra_msg
        return self

    def em(self, extra_msg):
        self.extra_msg = extra_msg
        return self


class Responses:
    OK = ResponseResult(200, 200, 'ok')
    NOT_OK = ResponseResult(500, 200, 'not everything is ok')

    MALFORMED_REQUEST = ResponseResult(400, 400, 'Malformed request')
    UNKNOWN_ACTION = ResponseResult(401, 400, 'Unknown action provided: ')
    MODEL_NOT_INITIALIZED = ResponseResult(402, 200, 'Model is not initialized. Make sure to call /api/init method')
    PARAMS_UNSATISFIED = ResponseResult(403, 400, 'Required params are not provided: ')
    USER_ITEM_NOT_FOUND = ResponseResult(404, 404, 'Combination of user_id/item_id is not found. '
                                                   'Did you forgot to execute api/add_user or api/add_item?')
    PARAMS_NOT_NUMERIC = ResponseResult(405, 400, 'Some of params are not numeric')
    USERS_ITEMS_NOT_AN_ARRAY = ResponseResult(406, 400, 'users and items have to be arrays')

    ONLINE_LEARN_FAILED = ResponseResult(501, 500, "Couldn't execute an online learning procedure successfully")
    NO_BACKEND_RESPONSE = ResponseResult(502, 500, 'No response from backend methods')

    def __init__(self):
        pass


def R(resp):
    return copy.copy(resp)


class RespError(ValueError):

    def __init__(self, *args, **kwargs):
        self.resp = None
        if len(args) > 0 and isinstance(args[0], ResponseResult):
            self.resp = R(args[0])
            if len(args) > 1:
                self.resp.msg += ''.join(args[1:])
        super(RespError, self).__init__(*args, **kwargs)