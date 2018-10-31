from logging import getLogger
from uzuwiki import settings

logger = getLogger(__name__)


class UzuWikiMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # user_digestがあれがログイン中。無ければ未ログイン。
        context['service_title'] = settings.SERVICE_TITLE

        # user_digestがあれがログイン中。無ければ未ログイン。
        context['is_login'] = True if 'user_digest' in self.request.session else False

        return context


class ReturnMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["return_url"] = self.request.session.get('last_request_url')

        return context


class LastRequestUrlMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 最終ログイン画面をセッションに保存
        self.request.session['last_request_url'] = self.request.path

        return context
