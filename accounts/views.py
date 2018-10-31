from django.views.generic import *
from uzuwiki.settings import AUTHENTICATION_BACKENDS
from social_core.backends.utils import get_backend
from .utils import load_strategy
from social_core.utils import sanitize_redirect
from django.urls import reverse
from logging import getLogger
from social_core.exceptions import AuthFailed
from social_core.exceptions import AuthCanceled
from ipware import get_client_ip
from commons.mixins import ReturnMixin
from accounts.mixins import LoginRequiredMixin
import hmac
import hashlib
from uzuwiki.settings import SECRET_KEY

logger = getLogger(__name__)


# Create your views here.
class IndexView(ReturnMixin, TemplateView):
    """
    表示画面
    """
    template_name = "accounts/index.html"


def auth(request, social_name):
    logger.debug("accounts.auth:start.social_name=%s", social_name)

    strategy = load_strategy(request)
    Backend = get_backend(AUTHENTICATION_BACKENDS, social_name)

    redirect_uri = reverse('accounts:complete', args=[social_name])

    logger.debug("redirect_uri=%s", redirect_uri)

    backend = Backend(strategy, redirect_uri)

    redirect_name = 'next'

    # Save any defined next value into session
    data = backend.strategy.request_data(merge=False)

    # Save extra data into session.
    for field_name in backend.setting('FIELDS_STORED_IN_SESSION', []):
        if field_name in data:
            backend.strategy.session_set(field_name, data[field_name])

    if redirect_name in data:
        # Check and sanitize a user-defined GET/POST next field value
        redirect_uri = data[redirect_name]
        if backend.setting('SANITIZE_REDIRECTS', True):
            allowed_hosts = backend.setting('ALLOWED_REDIRECT_HOSTS', []) + \
                            [backend.strategy.request_host()]
            redirect_uri = sanitize_redirect(allowed_hosts, redirect_uri)
        backend.strategy.session_set(
            redirect_name,
            redirect_uri or backend.setting('LOGIN_REDIRECT_URL')
        )

    logger.debug("backend.start")

    return backend.start()


class CompleteView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        strategy = load_strategy(self.request)

        Backend = get_backend(AUTHENTICATION_BACKENDS, kwargs.get("social_name"))
        redirect_uri = reverse('accounts:complete', args=[kwargs.get("social_name")])
        backend = Backend(strategy, redirect_uri)

        try:
            backend.process_error(backend.data)
        except(AuthFailed, AuthCanceled):
            logger.warning("認証失敗")
            return reverse('accounts:index')

        logger.debug("backend.data=%s", backend.data)

        state = backend.validate_state()
        data, params = None, None
        if backend.ACCESS_TOKEN_METHOD == 'GET':
            params = backend.auth_complete_params(state)
        else:
            data = backend.auth_complete_params(state)

        response = backend.request_access_token(
            backend.access_token_url(),
            data=data,
            params=params,
            headers=backend.auth_headers(),
            auth=backend.auth_complete_credentials(),
            method=backend.ACCESS_TOKEN_METHOD
        )

        try:
            backend.process_error(response)
        except(AuthFailed, AuthCanceled):
            logger.warning("認証失敗")
            return reverse('accounts:index')

        logger.debug("response=%s", response)

        user_data_response = backend.user_data(response["access_token"])
        user_details = backend.get_user_details(user_data_response)

        logger.debug("user_details=%s", user_details)

        self.request.session['social_name'] = kwargs.get("social_name")

        # self.request.session['username'] = user_details["username"]
        # self.request.session['email'] = user_details["email"]
        # self.request.session['fullname'] = user_details["fullname"]
        # self.request.session['first_name'] = user_details["first_name"]
        # self.request.session['last_name'] = user_details["last_name"]

        # OPEN_IDのＩＤをログインユーザを特定する一意キーとする。
        pkey = backend.get_user_id(user_details, user_data_response)

        if not pkey:
            logger.warning("認証失敗")
            return reverse('accounts:index')

        self.request.session['pkey'] = pkey

        # 一意キーをハッシュ化したものをユーザダイジェストとする。
        # 一意キーはメールアドレスだったりするので秘匿対象
        # ハッシュを破られないように注意
        user_digest = hmac.new(pkey.encode("UTF-8"), SECRET_KEY.encode("UTF-8"), hashlib.sha512).hexdigest()
        self.request.session['user_digest'] = user_digest

        client_ip, is_routable = get_client_ip(self.request)

        logger.info("ログイン情報：social_name=%s / user_digest=%s / client_ip=%s",
                    self.request.session['social_name'],
                    self.request.session['user_digest'],
                    client_ip)

        return_url = self.request.session.get('last_request_url')
        last_request_url = return_url if return_url else "/"

        return last_request_url


class LogoutView(ReturnMixin, TemplateView):
    """
    表示画面
    """
    template_name = "accounts/logout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 最終URLを退避
        last_request_url = self.request.session.get('last_request_url')

        # セッションをクリア
        self.request.session.flush()

        # 最終URLをセット
        self.request.session['last_request_url'] = last_request_url

        return context


class InfoView(ReturnMixin, LoginRequiredMixin, TemplateView):
    """
    表示画面
    """
    template_name = "accounts/info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_login'] = True

        context["user_digest"] = self.request.session.get('user_digest')
        context["social_name"] = self.request.session.get('social_name')
        context["pkey"] = self.request.session.get('pkey')
        context["return_url"] = self.request.session.get('last_request_url')

        return context

