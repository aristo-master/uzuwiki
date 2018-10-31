import os
import json
from datetime import datetime
from datetime import timedelta
from django import forms
from commons.file import file_utils
from commons import file_name_tools
from ipware import get_client_ip
from commons.markdown import markdown_tools
from commons.errors import PageNotFoundError
from django.core.exceptions import ValidationError
from uzuwiki.settings_file_engine import MAX_PAGE_SIZE, MAX_PAGE_SIZE_MESSAGE
from logging import getLogger

logger = getLogger(__name__)


def validate_page_size(value):
    # ページサイズが巨大過ぎないかチェック
    if len(value.encode()) > MAX_PAGE_SIZE:
        raise ValidationError(MAX_PAGE_SIZE_MESSAGE)


class PageBaseForm(forms.Form):
    """
    ページの作成・編集の共通フォーム
    """
    wiki_id = forms.CharField(label="ＷｉｋｉＩＤ")

    # ページ名のmax_lengthに明確な根拠は無く、Windowsファイルの絶対パスの長さが260文字であることを踏まえ、
    # それ以下で常識的な使用に問題無い程度のサイズとする。
    page_name = forms.CharField(label="ページ名", max_length=100)

    contents = forms.CharField(required=False, label="ページ内容", validators=[validate_page_size])

    def __init__(self, wiki_id, **kwargs):
        super().__init__(**kwargs)

        self.fields['wiki_id'].initial = wiki_id

    def put_page_file(self, timestamp):

        # wikiID
        wiki_id = self.data["wiki_id"]
        # ファイル名
        file_name = file_name_tools.page_name_to_file_name(self.data["page_name"])

        # ページ一覧ファイルを取得する。
        page_file = json.loads(file_utils.get_file(wiki_id, "pages.json"))

        # 内容が空になったら削除として扱う。
        # 一覧から見えなくなるだけでファイルや履歴は残る。
        status = "active" if self.data["contents"] else "inactive"

        # ページ一覧を更新する。
        # 新規作成の場合はレコードの新規追加、更新の場合はレコード更新。

        # 注意事項
        # ページ一覧は異なる新規登録・編集の操作から同時に更新される可能性がある。
        # （一つのファイルに対する更新処理の競合）
        # 競合が発生した場合は後勝ちになるため、
        # 「ページを新規追加したにも関わらず、ページ一覧に記載が無い」という状況が発生する余地がある。
        # このため新規作成 or 更新の判定は、どの画面から操作が行われたかではなく、
        # 一覧に対象ページが存在するかどうかで判定する。
        # 「ページ一覧に記載が無い」が発生した場合、同画面を空更新することで一覧に追記可能である。（運用回避）

        # ファイル中に該当ページがあった場合、更新する。
        for page in page_file["data"]["pages"]:

            if page["file_name"] == file_name:
                page["update"] = timestamp
                page["status"] = status
                page_file["update"] = timestamp
                file_utils.put_file(wiki_id, "pages.json", json.dumps(page_file))
                return

        # ファイル中に該当ページが無かった場合、新規追加する。
        page_file["data"]["pages"].append({
            "file_name": file_name,
            "extension": "md",
            "create": timestamp,
            "update": timestamp,
            "status": status
        })

        page_file["create"] = timestamp
        page_file["update"] = timestamp

        file_utils.put_file(wiki_id, "pages.json", json.dumps(page_file))

    class Meta:
        fields = ("contents", "wiki_id", "page_name")


class PageCreateForm(PageBaseForm):
    """
    新規作成フォーム
    """

    def clean_page_name(self):
        # wikiID
        wiki_id = self.data["wiki_id"]

        # ページ名
        page_name = self.cleaned_data['page_name']

        # NGword
        # URLのパスと重複するIDを禁止する。
        ngname = [
            "attachment", "attachments",
            "comment", "comments",
            "history", "histories",
            "maintenance", "maintenances",
            "page", "pages",
            "create", "copy", "list", "updates", "help", "sitemap.xml",
        ]

        page_dirs = file_name_tools.to_page_dirs(page_name)
        if page_dirs[0] in ngname:
            raise forms.ValidationError('対象のページ名は予約語であるため、使用出来ません。')

        # ファイル名
        file_name = file_name_tools.page_name_to_file_name(page_name)

        # ページ一覧
        page_file = json.loads(file_utils.get_file(wiki_id, "pages.json"))
        pages = page_file["data"]["pages"]

        # 新規作成するページが既に存在していないかチェック
        for page in pages:

            if file_name == page["file_name"]:
                raise forms.ValidationError("対象のページは既に存在しています。")

        return page_name

    def put(self, request):
        # リクエストからipアドレスを、セッションからログイン情報を取得するが、
        # 共に必ず取得出来るとは限らない。
        client_ip, is_routable = get_client_ip(request)
        client_ip = client_ip if client_ip else "0.0.0.0"

        user_digest = request.session.get('user_digest')
        user_digest = user_digest if user_digest else "anonymous"

        logger.info("登録者情報：user_digest=%s / client_ip=%s",
                    user_digest, client_ip)

        # wikiID
        wiki_id = self.data["wiki_id"]
        # ファイル名
        file_name = file_name_tools.page_name_to_file_name(self.data["page_name"])
        # タイムスタンプ
        timestamp = datetime.now().isoformat()

        # ページを保存する。
        # 初期登録される内容は新規作成画面の中にhiddenで記述されている。
        file_utils.put_file(wiki_id, file_name + ".md", self.data["contents"])

        # 設定ファイルの新規作成
        conf_file = {
            "file_type": "page_conf",
            "data": {
            },
            "confs": {
            },
            "created_at": timestamp,
            "updated_at": timestamp
        }

        # 設定ファイルを保存する。
        file_utils.put_file(wiki_id, file_name + ".confs.json", json.dumps(conf_file))

        # 履歴ファイルの新規作成
        history_file = {
            "file_type": "page_history",
            "histories": [
                {
                    "name": os.path.basename(file_name),
                    "timestamp": timestamp,
                    "comment": "created",
                    "client_ip": client_ip,
                    "user_digest": user_digest,
                }
            ],
            "created_at": timestamp,
            "updated_at": timestamp
        }

        # 履歴ファイルを保存する。
        file_utils.put_file(self.data["wiki_id"], file_name + ".histories.json", json.dumps(history_file))

        # ページ一覧を更新する。
        super().put_page_file(timestamp)


class PageCopyForm(PageCreateForm):
    """
    複写作成フォーム
    """

    def __init__(self, wiki_id, page_dirs, **kwargs):
        super().__init__(wiki_id=wiki_id, **kwargs)

        self.fields['page_name'].initial = file_name_tools.page_dirs_to_page_name(page_dirs) + "のコピー"

        # コンテンツ
        try:
            contents = markdown_tools.get_edit_contents(wiki_id, page_dirs)
            self.fields['contents'].initial = contents
        except PageNotFoundError:
            # ページが存在しない。
            pass


class PageUpdateForm(PageBaseForm):
    """
    更新フォーム
    """

    def __init__(self, wiki_id, page_dirs, **kwargs):
        super().__init__(wiki_id=wiki_id, **kwargs)

        self.fields['page_name'].initial = file_name_tools.page_dirs_to_page_name(page_dirs)

        # コンテンツ
        try:
            contents = markdown_tools.get_edit_contents(wiki_id, page_dirs)
            self.fields['contents'].initial = contents
        except PageNotFoundError:
            # ページが存在しない。
            pass

    def put(self, request):
        # リクエストからipアドレスを、セッションからログイン情報を取得するが、
        # 必ず取得出来るものではない。
        client_ip, is_routable = get_client_ip(request)
        client_ip = client_ip if client_ip else "0.0.0.0"

        user_digest = request.session.get('user_digest')
        user_digest = user_digest if user_digest else "anonymous"

        logger.info("更新者情報：user_digest=%s / client_ip=%s",
                    user_digest, client_ip)

        # wikiID
        wiki_id = self.data["wiki_id"]
        # ファイル名
        file_name = file_name_tools.page_name_to_file_name(self.data["page_name"])
        # タイムスタンプ
        timestamp = datetime.now().isoformat()

        # ページの履歴ファイルを取得
        history_file = file_utils.get_file(wiki_id, file_name + ".histories.json")
        history_file = json.loads(history_file)

        # 最後（現在）の履歴を取得
        last_history = history_file["histories"][-1]

        # 最終更新日時
        last_history_timestamp = datetime.strptime(last_history["timestamp"], "%Y-%m-%dT%H:%M:%S.%f")

        # 最終更新から一時間以内に再更新した場合、履歴を追加しない。
        # 「ちょっと更新して保存」を繰り返すことで残す価値の履歴が増えてしまうことを回避するための措置
        if last_history_timestamp > datetime.now() - timedelta(hours=1):

            # ページを保存する。
            file_utils.put_file(wiki_id, file_name + ".md", self.data["contents"])

            # 内容が空になったら削除として扱う。
            # 一覧から見えなくなるだけでファイルや履歴は残る。
            comment = "updated" if self.data["contents"] else "deleted"

            last_history["name"] = os.path.basename(file_name)
            last_history["timestamp"] = timestamp
            last_history["comment"] = comment
            last_history["client_ip"] = client_ip
            last_history["user_digest"] = user_digest

        else:

            # 現在のページをバックアップする。
            backup_file_name = file_name + "." + last_history_timestamp.strftime("%Y%m%d%H%M%S%f")
            file_utils.put_history(wiki_id, file_name + ".md", backup_file_name + ".md")

            # ページを保存する。
            file_utils.put_file(wiki_id, file_name + ".md", self.data["contents"])

            # バックアップ情報を履歴に追記する。
            last_history["history_file_path"] = backup_file_name + ".md"
            history_file["histories"][-1] = last_history

            # 内容が空になったら削除として扱う。
            # 一覧から見えなくなるだけでファイルや履歴は残る。
            comment = "updated" if self.data["contents"] else "deleted"

            # 新しい履歴を追加する。
            history_file["histories"].append({
                "name": os.path.basename(file_name),
                "timestamp": timestamp,
                "comment": comment,
                "client_ip": client_ip,
                "user_digest": user_digest,
            })

        history_file["updated_at"] = timestamp

        # 履歴ファイルを更新する。
        file_utils.put_file(wiki_id, file_name + ".histories.json", json.dumps(history_file))

        # ページ一覧を更新する。
        super().put_page_file(timestamp)
