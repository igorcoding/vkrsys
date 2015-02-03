class ResponseResult:
    def __init__(self, code, status, msg):
        self.code = code
        self.status = status
        self.msg = msg

    def to_res(self):
        return (self.status, {
            'code': self.code,
            'msg': self.msg
        })

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            self.msg += str(args[0])


class Responses:
    OK = ResponseResult(200, 200, 'ok')
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


class RespError(ValueError):

    def __init__(self, *args, **kwargs):
        self.resp = None
        if len(args) > 0 and isinstance(args[0], ResponseResult):
            self.resp = args[0]
            if len(args) > 1:
                self.resp.msg += ''.join(args[1:])
        super(RespError, self).__init__(*args, **kwargs)