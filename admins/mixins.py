from logging import getLogger
from django.http import HttpResponseNotAllowed
from uzuwiki.settings import TOTAL_MANAGER_DIGEST

logger = getLogger(__name__)


class TotalManagerOnlyMixin:

    def dispatch(self, request, *args, **kwargs):

        if request.session.get("user_digest") not in TOTAL_MANAGER_DIGEST.split():
            return HttpResponseNotAllowed()

        return super().dispatch(request, *args, **kwargs)
