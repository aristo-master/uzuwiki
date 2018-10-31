import json
from commons.file import file_utils
from logging import getLogger
from django.urls import reverse
from django.contrib import messages
from wikis.mixins import WikiMixin
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotFound

logger = getLogger(__name__)


class LoginRequiredMixin():

    def dispatch(self, request, *args, **kwargs):
        if not "user_digest" in request.session:
            messages.add_message(self.request, messages.INFO, 'ログインして下さい。')
            return HttpResponseRedirect(reverse('accounts:index'))

        return super().dispatch(request, *args, **kwargs)
