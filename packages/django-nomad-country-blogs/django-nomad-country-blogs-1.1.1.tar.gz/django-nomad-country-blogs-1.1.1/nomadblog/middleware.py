from django.conf import settings


class CountryCode(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Country code in URL
        country_code = view_kwargs.get('country_code')
        # Country code in session, fallback to default country
        if not country_code:
            country_code = request.session.get('country_code', settings.DEFAULT_COUNTRY_CODE)
        request.session['country_code'] = country_code
