from django.views.generic import *
from wikis.mixins import *
from commons import file_name_tools
from .forms import FileUploadFileForm
from django.urls import reverse
from wikis.attachments import attachment_tool
import datetime
from logging import getLogger

logger = getLogger(__name__)


# Create your views here.

class AttachmentView(PageMixin, FormView):
    """
    ファイルの添付
    """
    form_class = FileUploadFileForm
    template_name = "wikis/attachments/attachment.html"
    mode = "edit"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['wiki_id'] = self.request.wiki_id
        kwargs['page_dirs'] = self.request.page_dirs

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ページのファイルパスを取得
        file_name = file_name_tools.page_dirs_to_file_name(self.request.page_dirs)

        # 添付ファイル一覧を取得
        attachment_file_data = attachment_tool.get_or_new(self.request.wiki_id, file_name)

        attachments = attachment_file_data["attachments"]

        for attachment in attachments:
            attachment["timestamp"] = datetime.datetime.strptime(attachment["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")

        context["attachments"] = attachments

        return context

    def form_valid(self, form):
        # ページ新規作成
        form.put(self.request)

        return super().form_valid(form)

    def get_success_url(self):
        form = super().get_form()

        argzz = [form.data["wiki_id"]]
        argzz.extend(file_name_tools.to_page_dirs(form.data["page_name"]))

        return reverse('wikis.attachments:attachment', args=argzz)
