VERSION = (1, 4, 0)
__version__ = '.'.join(map(str, VERSION))


def get_post_model():
    """
    Returns the Post model that is active in this project.
    """
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    from django.db.models import get_model
    POST_MODEL = getattr(settings, 'POST_MODEL', 'nomadblog.Post')
    try:
        app_label, model_name = POST_MODEL.split('.')
    except ValueError:
        raise ImproperlyConfigured("POST_MODEL must be of the form 'app_label.model_name'")
    model = get_model(app_label, model_name)
    if model is None:
        raise ImproperlyConfigured("POST_MODEL refers to model '%s' that has not been installed" % POST_MODEL)
    return model
