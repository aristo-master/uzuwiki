from django.views.generic import *
from uzuwiki.settings_static_file_engine import *
from django.urls import reverse
from commons.mixins import UzuWikiMixin
from admins.mixins import TotalManagerOnlyMixin
from uzuwiki.settings import TOTAL_MANAGER_DIGEST
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import FlowExchangeError
from django.contrib import messages
from oauth2client.file import Storage
from logging import getLogger
from commons.file import file_utils
import tempfile
import os

logger = getLogger(__name__)

GOOGLE_CREDENTIALS_SCOPE = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.install', ]


# Create your views here.
class IndexView(UzuWikiMixin, TemplateView):
    """
    新規作成画面
    """
    template_name = "admins/index.html"

    def get_template_names(self):

        if self.request.session.get("user_digest") not in TOTAL_MANAGER_DIGEST.split():
            return ["admins/not_admin.html"]
        else:
            return super().get_template_names()


class GoogleCredentialsView(UzuWikiMixin, TotalManagerOnlyMixin, TemplateView):
    """
    新規作成画面
    """
    template_name = "admins/google_credentials.html"


class GoogleCredentialsDoView(UzuWikiMixin, TotalManagerOnlyMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        redirect_uri = "{}://{}{}".format(
            self.request.get_raw_uri().split(":")[0]
            , self.request.get_host()
            , reverse("admins:google_credentials_complete"))

        flow = OAuth2WebServerFlow(client_id=GOOGLE_CREDENTIALS_CLIENT_ID,
                                   client_secret=GOOGLE_CREDENTIALS_CLIENT_SECRET,
                                   scope=GOOGLE_CREDENTIALS_SCOPE,
                                   redirect_uri=redirect_uri,
                                   access_type='offline',
                                   approval_prompt='force')

        authorize_url = flow.step1_get_authorize_url()

        logger.debug("authorize_url=%s", authorize_url)
        return authorize_url


class GoogleCredentialsCompleteView(UzuWikiMixin, TotalManagerOnlyMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        code = self.request.GET.get("code")

        redirect_uri = "{}://{}{}".format(
            self.request.get_raw_uri().split(":")[0]
            , self.request.get_host()
            , reverse("admins:google_credentials_complete"))

        flow = OAuth2WebServerFlow(client_id=GOOGLE_CREDENTIALS_CLIENT_ID,
                                   client_secret=GOOGLE_CREDENTIALS_CLIENT_SECRET,
                                   scope=GOOGLE_CREDENTIALS_SCOPE,
                                   redirect_uri=redirect_uri,
                                   access_type='offline',
                                   approval_prompt='force')

        try:
            credentials = flow.step2_exchange(code)

            # credentialsが無効かどうかの判定
            if not credentials or credentials.invalid:
                messages.add_message(self.request, messages.WARNING, '認証に失敗しました。')

            temp = tempfile.TemporaryDirectory()
            credentials_path = os.path.join(temp.name, 'credentials.json')

            logger.debug("credentials_path=%s", credentials_path)

            storage = Storage(credentials_path)
            storage.put(credentials)

            with open(credentials_path, encoding="utf-8") as f:
                file_utils.put_root_file('credentials.json', f.read())

            messages.add_message(self.request, messages.WARNING, '認証に成功しました。')

            return reverse("admins:google_credentials")

        except FlowExchangeError as e:
            messages.add_message(self.request, messages.WARNING, '認証に失敗しました。')

        return reverse("admins:google_credentials")
