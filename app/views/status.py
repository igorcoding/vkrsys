from django.conf import settings

_STATUS = {
    'ok': (200, 'ok'),
    'token_expired': (501, 'your token has been expired'),
    'unknown': (500, 'unknown error'),
    'absent': (400, 'required params are not present'),
    'unauthorized': (401, 'unauthorized')
}

STATUS = dict(zip(_STATUS.keys(), map(lambda v: v[0], _STATUS.values())))
MSG = dict(zip(_STATUS.keys(), map(lambda v: v[0], _STATUS.values())))

REDIRECT_RESPONSE = {
    'status': STATUS['unauthorized'],
    'msg': MSG['unauthorized'],
    'redirect_url': settings.VK_LOGIN_URL
}