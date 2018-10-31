import json
from commons.file import file_utils
from logging import getLogger
from django.urls import reverse
from django.contrib import messages
from wikis.mixins import WikiMixin
from django.http import HttpResponseRedirect
from uzuwiki import settings

logger = getLogger(__name__)


class ManagerRequiredMixin(WikiMixin):

    def dispatch(self, request, *args, **kwargs):

        self.initialize(request, *args, **kwargs)

        if not "user_digest" in request.session:
            messages.add_message(self.request, messages.INFO, '管理機能を使う場合は管理者にてログインして下さい。')
            return HttpResponseRedirect(reverse('accounts:index'))

        user_digest = self.request.session["user_digest"]

        if user_digest not in settings.TOTAL_MANAGER_DIGEST.split() and request.wiki_conf["manager"] != user_digest:
            messages.add_message(self.request, messages.INFO, 'このアカウントは管理者ではありません。管理機能を使う場合はログアウトし、管理者にてログインして下さい。')
            return HttpResponseRedirect(reverse('accounts:info'))

        return super().dispatch(request, *args, **kwargs)
