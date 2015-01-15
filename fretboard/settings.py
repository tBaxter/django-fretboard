from django.conf import settings
from django.contrib.sites.models import Site

def current_site():
    """
    Helper function to play nice with appconfig loading.
    """
    return Site.objects.get_current()


PAGINATE_BY = getattr(settings, "PAGINATE_BY", 25)
FORUM_BASE_NAME  = getattr(settings, 'FORUM_BASE_NAME', current_site.name)
COMMENT_PLACEHOLDER = getattr(settings, "COMMENT_PLACEHOLDER", "Be nice.")
