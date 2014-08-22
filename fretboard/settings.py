from django.conf import settings
from django.contrib.sites.models import Site

PAGINATE_BY = getattr(settings, "PAGINATE_BY", 25)
FORUM_BASE_NAME  = getattr(settings, 'FORUM_BASE_NAME', Site.objects.get_current().name)
COMMENT_PLACEHOLDER = getattr(settings, "COMMENT_PLACEHOLDER", "Be nice.")
