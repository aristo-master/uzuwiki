import json
from datetime import datetime
from django import forms
from commons.file import file_utils
from commons import file_name_tools
from wikis.comments import comment_tool
from logging import getLogger

logger = getLogger(__name__)


class CommentForm(forms.Form):
    """
    コメントフォーム
    """
    wiki_id = forms.CharField(label="ＷｉｋｉＩＤ")
    page_name = forms.CharField(label="ページ名")
    parent = forms.IntegerField(label="親ＩＤ")
    name = forms.CharField(required=False, label="名前", max_length=64)
    body = forms.CharField(label="コメント", max_length=1280)

    def __init__(self, page_dirs, **kwargs):
        super().__init__(**kwargs)

        self.fields['page_name'].initial = file_name_tools.page_dirs_to_page_name(page_dirs)
        self.fields['name'].initial = ""
        self.fields['body'].initial = ""

    def put(self):
        # ページのファイルパスを取得
        file_name = file_name_tools.page_name_to_file_name(self.data["page_name"])

        # コメントデータを取得
        comment_file_data = comment_tool.get_or_new(self.data["wiki_id"], file_name)

        # タイムスタンプ
        timestamp = datetime.now().isoformat()

        # 匿名の場合は名無しさんとする
        name = self.data["name"] if self.data["name"] else "名無しさん"

        # 次のシーケンス番号
        next_id = len(comment_file_data["comments"]) + 1

        comment_file_data["comments"].append({
            "id": next_id,
            "name": name,
            "body": self.data["body"],
            "timestamp": datetime.now().isoformat(),
            "parent": int(self.data["parent"])
        })

        if not "created_at" in comment_file_data:
            comment_file_data["created_at"] = timestamp

        comment_file_data["updated_at"] = timestamp

        # コメントファイルを保存する。
        file_utils.put_file(self.data["wiki_id"], file_name + ".comments.json", json.dumps(comment_file_data))

        page_conf_file = file_utils.get_file(self.data["wiki_id"], file_name + ".confs.json")
        page_conf = json.loads(page_conf_file)

        page_conf["confs"]["comment_exist_flg"] = True

        file_utils.put_file(self.data["wiki_id"], file_name + ".confs.json", json.dumps(page_conf))

    class Meta:
        fields = ("wiki_id", "page_name", "parent", "name", "body")
