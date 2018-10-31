from django.views.generic import *
from commons.file import file_utils
from roots.forms import CreateForm
from django.urls import reverse
from commons.mixins import UzuWikiMixin, ReturnMixin, LastRequestUrlMixin
from django.contrib import messages
import datetime
from commons import file_name_tools
from django.http import HttpResponse
from django.template.loader import render_to_string
from uzuwiki import settings
import json


# Create your views here.
class IndexView(UzuWikiMixin, LastRequestUrlMixin, TemplateView):
    template_name = "roots/index.html"

    def get_context_data(self, **kwargs):
        # 最終ログイン画面をセッションに保存
        self.request.session['last_request_url'] = self.request.path
        context = super().get_context_data(**kwargs)

        wikis_file = file_utils.get_root_file("wikis.json")
        wikis_file = json.loads(wikis_file)

        context["wiki_list"] = wikis_file["data"]

        return context


class CreateView(UzuWikiMixin, FormView):
    """
    新規作成画面
    """
    form_class = CreateForm
    template_name = "roots/create.html"

    def form_valid(self, form):
        if not 'user_digest' in self.request.session:
            messages.add_message(self.request, messages.ERROR, 'ログイン情報を取得出来ませんでした。')
            return self.render_to_response(self.get_context_data(form=form))

        # ページ新規作成
        form.create(self.request)

        return super().form_valid(form)

    def get_template_names(self):

        if not 'user_digest' in self.request.session:
            return ["roots/create_not_login.html"]

        if settings.PRIVATE_MODE:

            if not 'user_digest' in self.request.session:
                return ["roots/create_not_login.html"]

            if self.request.session["user_digest"] not in settings.TOTAL_MANAGER_DIGEST.split():
                return ["roots/create_total_manager_only.html"]

        else:

            if not 'user_digest' in self.request.session:
                return ["roots/create_not_login.html"]

        return super().get_template_names()

    def get_success_url(self):
        form = super().get_form()

        argzz = [form.data["wiki_id"]]

        return reverse('wikis.pages:index', args=argzz)


class AgreementView(UzuWikiMixin, ReturnMixin, TemplateView):
    """
    利用規約
    """
    template_name = "roots/agreement.html"


class PrivacyView(UzuWikiMixin, ReturnMixin, TemplateView):
    """
    プライバシーポリシー
    """
    template_name = "roots/privacy.html"


def sitemap(request):
    wikis_file = file_utils.get_root_file("wikis.json")
    wikis_file = json.loads(wikis_file)

    datas = wikis_file["data"]

    wikis = []
    for data in datas.keys():
        wiki = {}

        argzz = [data]

        loc = "{}://{}{}".format(
            request.get_raw_uri().split(":")[0]
            , request.get_host()
            , reverse('wikis.pages:sitemap', args=argzz))

        wiki["loc"] = loc
        wikis.append(wiki)

    context = {"wikis": wikis}

    html = render_to_string("roots/sitemapindex.xml", context)

    return HttpResponse(html, content_type="application/xhtml+xml")
