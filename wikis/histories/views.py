from django.views.generic import *
from wikis.mixins import *
import json
import difflib
from datetime import datetime
from commons.markdown import markdown_tools
from commons import file_name_tools
from commons.file import file_utils
from logging import getLogger

logger = getLogger(__name__)


class HistoryView(PageMixin, TemplateView):
    """
    履歴画面
    """
    template_name = "wikis/histories/history.html"
    mode = "history"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ページの設定ファイルを取得
        file_name = file_name_tools.page_dirs_to_file_name(super().get_page_dirs())
        history_file = file_utils.get_file(self.request.wiki_id, file_name + ".histories.json")
        history_file = json.loads(history_file)

        history_before = None
        for history in history_file["histories"]:

            if history_before:
                history["before_history_file_path"] = history_before["history_file_path"]

            history["timestamp"] = datetime.strptime(history["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")
            history_before = history

        context["history_file"] = history_file

        return context


class DiffView(PageMixin, TemplateView):
    """
    差分画面
    """
    template_name = "wikis/histories/diff.html"
    mode = "history"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("before_history_file_path"):

            before_history_file_path = self.request.GET.get("before_history_file_path")
            before_history_file = file_utils.get_history_file(self.request.wiki_id, before_history_file_path)

            history_file_path = self.request.GET.get("history_file_path")
            history_file = file_utils.get_history_file(self.request.wiki_id, history_file_path)

            from_lines = before_history_file.splitlines(keepends=True)
            to_lines = history_file.splitlines(keepends=True)

        else:

            history_file_path = self.request.GET.get("history_file_path")
            history_file = file_utils.get_history_file(self.request.wiki_id, history_file_path)

            latest_file = markdown_tools.get_edit_contents(self.request.wiki_id, self.request.page_dirs)

            from_lines = history_file.splitlines(keepends=True)
            to_lines = latest_file.splitlines(keepends=True)

        # differ = Differ()
        # diff = differ.compare(from_lines, to_lines)
        diff = difflib.context_diff(from_lines, to_lines)
        diff = ''.join(diff)

        context["diffs"] = diff.splitlines()

        return context


class SrcView(PageMixin, TemplateView):
    """
    編集画面
    """
    template_name = "wikis/histories/src.html"
    mode = "history"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        history_file_path = self.request.GET.get("history_file_path")
        history_file = file_utils.get_history_file(self.request.wiki_id, history_file_path)

        context["history_file"] = history_file

        return context
