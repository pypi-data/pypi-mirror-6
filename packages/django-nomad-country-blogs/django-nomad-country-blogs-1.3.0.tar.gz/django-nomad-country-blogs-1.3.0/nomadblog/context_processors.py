from django.conf import settings


def country_code(request):
    return {'country_code': request.session.get('country_code', settings.DEFAULT_COUNTRY_CODE)}
