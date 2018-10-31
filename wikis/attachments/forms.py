import json
from django import forms
from commons.file import file_utils
from commons import file_name_tools
from wikis.attachments import attachment_tool
from django.core.exceptions import ValidationError
from datetime import datetime
from uzuwiki.settings_static_file_engine import MAX_FILE_SIZE, MAX_FILE_SIZE_MESSAGE
from logging import getLogger

logger = getLogger(__name__)


def validate_attachment_file_size(file):
    # ページサイズが巨大過ぎないかチェック
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(MAX_FILE_SIZE_MESSAGE)


class FileUploadFileForm(forms.Form):
    wiki_id = forms.CharField(label="ＷｉｋｉＩＤ")
    page_name = forms.CharField(label="ページ名")
    file = forms.FileField(label="ファイル", validators=[validate_attachment_file_size])

    def __init__(self, wiki_id, page_dirs, **kwargs):
        super().__init__(**kwargs)

        self.fields['wiki_id'].initial = wiki_id
        self.fields['page_name'].initial = file_name_tools.page_dirs_to_page_name(page_dirs)

    def put(self, request):
        file = request.FILES['file']

        # ページのファイルパスを取得
        file_name = file_name_tools.page_name_to_file_name(self.data["page_name"])

        # 添付ファイル一覧を取得
        attachment_file_data = attachment_tool.get_or_new(self.data["wiki_id"], file_name)

        # 添付ファイルを保存する。
        record = file_utils.put_static_file(self.data["wiki_id"], file.name, file)

        attachment_file_data["attachments"].append(record)

        timestamp = datetime.now().isoformat()

        if "created_at" not in attachment_file_data:
            attachment_file_data["created_at"] = timestamp

        attachment_file_data["updated_at"] = timestamp

        # 添付ファイルを保存する。
        file_utils.put_file(self.data["wiki_id"], file_name + ".attachments.json", json.dumps(attachment_file_data))

    class Meta:
        fields = ("wiki_id", "page_name", "file")
