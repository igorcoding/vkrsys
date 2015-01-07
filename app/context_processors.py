from django.conf import settings


def production_state(request):
    return dict(PRODUCTION=settings.PRODUCTION)