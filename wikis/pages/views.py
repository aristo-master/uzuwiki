from django.views.generic import *
from wikis.mixins import *
import json
from commons.markdown import markdown_tools
from commons import file_name_tools
from commons.file import file_utils
from .forms import PageCreateForm, PageUpdateForm, PageCopyForm
from django.urls import reverse
import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from logging import getLogger

logger = getLogger(__name__)


class IndexView(RedirectView):
    """
    TOPページへのアクセスはFrontPageにリダイレクトする。
    """

    def get_redirect_url(self, *args, **kwargs):
        wiki_id = kwargs.get("wiki_id")

        argzz = [wiki_id, "FrontPage"]

        return reverse('wikis.pages:show', args=argzz)


class ShowView(PageMixin, CommentFlgMixin, TemplateView):
    """
    ページの表示
    """
    template_name = "wikis/pages/show.html"
    mode = "show"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # コンテンツ
        context["main_contents"] = markdown_tools.get_contents(self.request.wiki_id, self.request.page_dirs)

        return context


class CreateView(ModeMixin, EditAuthorityMixin, FormView):
    """
    ページの新規作成
    """
    form_class = PageCreateForm
    template_name = "wikis/pages/create.html"
    mode = "create"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['wiki_id'] = self.request.wiki_id

        return kwargs

    def form_valid(self, form):
        # ページ新規作成
        form.put(self.request)

        return super().form_valid(form)

    def get_success_url(self):
        form = super().get_form()

        argzz = [form.data["wiki_id"]]
        argzz.extend(file_name_tools.to_page_dirs(form.data["page_name"]))

        return reverse('wikis.pages:show', args=argzz)


class EditView(PageMixin, EditAuthorityMixin, FormView):
    """
    ページの編集
    ページが凍結中の場合は凍結画面を表示する。
    """
    form_class = PageUpdateForm
    template_name = "wikis/pages/edit.html"
    mode = "edit"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['wiki_id'] = self.request.wiki_id
        kwargs['page_dirs'] = self.request.page_dirs

        return kwargs

    def form_valid(self, form):
        # ページ更新
        form.put(self.request)

        return super().form_valid(form)

    def get_success_url(self):
        form = super().get_form()

        argzz = [form.data["wiki_id"]]
        argzz.extend(file_name_tools.to_page_dirs(form.data["page_name"]))

        return reverse('wikis.pages:show', args=argzz)

    def get_template_names(self):
        if self.request.page_conf["confs"].get("freeze_mode") == "1":
            return ["wikis/pages/freeze.html"]
        else:
            return super().get_template_names()


class CopyView(PageMixin, EditAuthorityMixin, FormView):
    """
    ページをコピーして新規作成
    コピーしたいページを表示した状態で[複写]を選択することで遷移出来る。
    """
    form_class = PageCopyForm
    template_name = "wikis/pages/copy.html"
    mode = "copy"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['wiki_id'] = self.request.wiki_id
        kwargs['page_dirs'] = self.request.page_dirs

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # コンテンツ
        context["main_contents"] = markdown_tools.get_contents(self.request.wiki_id, self.request.page_dirs)

        return context

    def form_valid(self, form):
        # ページ新規作成
        form.put(self.request)

        return super().form_valid(form)

    def get_success_url(self):
        form = super().get_form()

        argzz = [form.data["wiki_id"]]
        argzz.extend(file_name_tools.to_page_dirs(form.data["page_name"]))

        return reverse('wikis.pages:show', args=argzz)


class ListView(PageMixin, TemplateView):
    """
    ページの一覧
    ファイル名の昇順で全ページを表示する。
    """
    template_name = "wikis/pages/list.html"
    mode = "list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 一覧ファイル取得
        pages = json.loads(file_utils.get_file(self.request.wiki_id, "pages.json"))
        pages = pages["data"]["pages"]
        pages = sorted(pages, key=lambda x: x['file_name'])

        for page in pages:
            file_name_slash = file_name_tools.file_name_to_page_name(page["file_name"])
            page["file_name"] = file_name_slash

            argzz = [self.request.wiki_id]
            argzz.extend(file_name_slash.split("/"))
            page["url"] = reverse('wikis.pages:show', args=argzz)

            page["update"] = datetime.datetime.strptime(page["update"], "%Y-%m-%dT%H:%M:%S.%f")

        context["pages"] = pages

        return context


class UpdatesView(PageMixin, TemplateView):
    """
    ページの一覧
    更新日時の降順で表示する。
    """
    template_name = "wikis/pages/updates.html"
    mode = "list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 一覧ファイル取得
        pages = json.loads(file_utils.get_file(self.request.wiki_id, "pages.json"))
        pages = pages["data"]["pages"]
        pages = sorted(pages, key=lambda x: x['update'], reverse=True)

        for page in pages:
            file_name_slash = file_name_tools.file_name_to_page_name(page["file_name"])
            page["file_name"] = file_name_slash

            argzz = [self.request.wiki_id]
            argzz.extend(file_name_slash.split("/"))
            page["url"] = reverse('wikis.pages:show', args=argzz)

            tdatetime = datetime.datetime.strptime(page["update"], '%Y-%m-%dT%H:%M:%S.%f')
            page["update_day"] = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day)
            page["update"] = tdatetime

        context["pages"] = pages

        return context


class HelpView(ModeMixin, TemplateView):
    """
    ヘルプ画面
    """
    template_name = "wikis/pages/help.html"
    mode = "help"


def sitemap(request, wiki_id):
    page_file = json.loads(file_utils.get_file(wiki_id, "pages.json"))
    pages = page_file["data"]["pages"]
    pages = sorted(pages, key=lambda x: x['update'], reverse=True)

    for page in pages:
        file_name_slash = file_name_tools.file_name_to_page_name(page["file_name"])
        page["file_name"] = file_name_slash

        argzz = [wiki_id]
        argzz.extend(file_name_slash.split("/"))

        loc = "{}://{}{}".format(
            request.get_raw_uri().split(":")[0]
            , request.get_host()
            , reverse('wikis.pages:show', args=argzz))

        page["loc"] = loc

        tdatetime = datetime.datetime.strptime(page["update"], '%Y-%m-%dT%H:%M:%S.%f')
        tdate = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day).strftime('%Y-%m-%dT%H:%M:%SZ')
        page["lastmod"] = tdate

    context = {"wiki_id": wiki_id, "pages": pages}

    html = render_to_string("wikis/pages/sitemap.xml", context)

    return HttpResponse(html, content_type="application/xhtml+xml")
