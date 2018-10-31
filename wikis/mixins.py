import json
from commons import file_name_tools
from commons.file import file_utils
from uzuwiki.settings import hierarchy_count
from commons.mixins import UzuWikiMixin
from commons.mixins import LastRequestUrlMixin
from django.http import HttpResponseNotFound
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from uzuwiki import settings
from logging import getLogger

logger = getLogger(__name__)


class WikiMixin(UzuWikiMixin, LastRequestUrlMixin):

    def initialize(self, request, *args, **kwargs):

        if hasattr(self.request, "initialized_flg"):
            return

        self.request.initialized_flg = True

        my_kwargs = self.get_my_kwargs(**kwargs)

        request.wiki_id = my_kwargs.get("wiki_id")

        try:
            wiki_conf_file = file_utils.get_file(request.wiki_id, "config.json")
            request.wiki_conf = json.loads(wiki_conf_file)

        except FileNotFoundError:

            request.wiki_conf = None

    def dispatch(self, request, *args, **kwargs):

        self.initialize(request, *args, **kwargs)

        if not request.wiki_conf:
            return HttpResponseNotFound()

        # 公開範囲(管理人にのみ、表示を許可するモード場合のチェック)
        if request.wiki_conf["confs"].get("release_status") == "1":

            if not "user_digest" in request.session:
                messages.add_message(self.request, messages.WARNING, '管理人でログインして下さい。')
                return HttpResponseRedirect(reverse('accounts:index'))

            user_digest = self.request.session["user_digest"]

            if request.wiki_conf["manager"] != user_digest:
                messages.add_message(self.request, messages.WARNING, '管理人でログインして下さい。')
                return HttpResponseRedirect(reverse('accounts:info'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["wiki_id"] = self.request.wiki_id
        context["wiki_conf"] = self.request.wiki_conf
        context["host"] = self.request.get_host()

        user_digest = self.request.session.get("user_digest")
        context["user_digest"] = user_digest

        # 管理人フラグ
        if user_digest in settings.TOTAL_MANAGER_DIGEST.split():
            context["wiki_manager_flg"] = True

        elif self.request.wiki_conf["manager"] == user_digest:
            context["wiki_manager_flg"] = True

        else:
            context["wiki_manager_flg"] = False

        return context

    def get_my_kwargs(self, **kwargs):

        if "wiki_id" in kwargs:
            return kwargs
        else:
            return self.kwargs


class ModeMixin(WikiMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mode"] = self.mode

        return context


class PageMixin(ModeMixin):

    def initialize(self, request, *args, **kwargs):

        if hasattr(self.request, "initialized_flg"):
            return

        super().initialize(request, *args, **kwargs)

        self.request.page_dirs = self.get_page_dirs(**kwargs)

        try:
            page_conf_file = file_utils.get_file(
                request.wiki_id,
                file_name_tools.page_dirs_to_file_name(request.page_dirs) + ".confs.json")

            request.page_conf = json.loads(page_conf_file)

        except FileNotFoundError:

            request.page_conf = None

    def dispatch(self, request, *args, **kwargs):

        logger.debug("PageMixin.dispatch:start")

        self.initialize(request, *args, **kwargs)

        if not request.page_conf:
            return HttpResponseNotFound()

        logger.debug("PageMixin.dispatch:end")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["page_dirs"] = self.request.page_dirs
        context["page_name"] = file_name_tools.page_dirs_to_page_name(self.request.page_dirs)
        context["page_title"] = self.request.page_dirs[len(self.request.page_dirs) - 1]
        context["page_conf"] = self.request.page_conf

        return context

    def get_page_dirs(self, **kwargs):

        my_kwargs = super().get_my_kwargs(**kwargs)
        page_dirs = []
        for hierarchy in range(0, hierarchy_count):
            page_name = my_kwargs.get("page_name_" + str(hierarchy))
            if page_name:
                page_dirs.append(page_name)

        if not page_dirs:
            page_dirs.append("FrontPage")

        return page_dirs


class CommentFlgMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["comment_flg"] = True

        # Wiki全体でコメント禁止だった場合、コメントフラグをFalseにする
        if self.request.wiki_conf["confs"].get("comment_mode") == "1":
            context["comment_flg"] = False

        # このページがコメント禁止だった場合、コメントフラグをFalseにする
        if self.request.page_conf["confs"].get("comment_mode") == "1":
            context["comment_flg"] = False

        return context


class EditAuthorityMixin():
    """
    編集権限のチェック
    ・誰でも匿名でWikiを編集出来る(デフォルト)
    ・ログインしている人にのみ、編集を許可する
    ・管理人のみ、編集を許可する
    """

    def get_template_names(self):

        edit_authority = self.request.wiki_conf["confs"].get("edit_authority")

        if not edit_authority:
            return super().get_template_names()

        if edit_authority == "0":
            return super().get_template_names()

        if edit_authority == "1":

            # ログインしている人にのみ、編集を許可する
            if not 'user_digest' in self.request.session:
                return ["wikis/pages/no_edit_authority.html"]

        if edit_authority == "2":
            # 管理人のみ、編集を許可する
            if not "user_digest" in self.request.session:
                return ["wikis/pages/no_edit_authority.html"]

            user_digest = self.request.session["user_digest"]

            if self.request.wiki_conf["manager"] != user_digest:
                return ["wikis/pages/no_edit_authority.html"]

        return super().get_template_names()
