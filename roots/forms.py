import json
from datetime import datetime
from django import forms
from commons.file import file_utils
import re
from ipware import get_client_ip
from django.template.loader import render_to_string
from logging import getLogger

logger = getLogger(__name__)


class CreateForm(forms.Form):
    wiki_id = forms.CharField(max_length=30, min_length=2, label="ＷｉｋｉＩＤ", initial="")

    def clean_wiki_id(self):
        """
        wiki_idのバリデーションチェックは以下。
        ・必須
        ・最小２文字
        ・最大３０文字
        ・半角英数と「-(ハイフン)」「_(アンダーバー)」だけ使用可能。
        最小文字数の根拠は、「ＤＱ」や「ＦＦ」など、現実的な略称として一番短いのは２文字だと思った。
        最大文字数の根拠は無い。現実的用途として十分長く、かつ長過ぎてシステムが破壊されなければ良い。
        使用可能文字が半角英数と「-(ハイフン)」「_(アンダーバー)」だけなのは、変なＩＤを作る事を許容すると
        ユーザが不便するかもしれないと考えたため。
        URLエンコードされるので技術的には本来どんな文字（平仮名とか）でも入力可能である。
        :return: wiki_id
        """
        wiki_id = self.cleaned_data['wiki_id']

        pattern = r"^[a-z][a-z0-9_-]*$"
        matchOB = re.match(pattern, wiki_id)

        if not matchOB:
            raise forms.ValidationError('WikiIDに使用可能な文字は半角英小文字と数字、「-(ハイフン)」、「_(アンダーバー)」です。先頭は半角英小文字として下さい。')

        # NGword
        # URLのパスと重複するIDを禁止する。
        # 念のため、ディレクトリ名と被ってしまうものも禁止しておく。
        ngname = [
            "account", "accounts",
            "admin", "admins",
            "common", "commons",
            "root", "roots",
            "uzuwiki", "uzuwikis",
            "webapi", "webapis",
            "wiki", "wikis",
            "static", "statics",
            "page", "pages",
        ]

        if wiki_id in ngname:
            raise forms.ValidationError('対象のWikiIDは予約語であるため、使用出来ません。')

        # wikiファイル取得
        wikis_file = file_utils.get_root_file("wikis.json")
        wikis_file = json.loads(wikis_file)

        if wiki_id in wikis_file["data"]:
            raise forms.ValidationError("対象のWikiIDは使用されています。")

        return wiki_id

    def create(self, request):
        wiki_id = self.data["wiki_id"]

        # タイムスタンプ
        timestamp = datetime.now().isoformat()

        context = {}
        context["wiki_id"] = wiki_id
        context["timestamp"] = timestamp
        context["user_digest"] = request.session["user_digest"]

        client_ip, is_routable = get_client_ip(request)
        client_ip = client_ip if client_ip else "0.0.0.0"
        context["client_ip"] = client_ip

        # ディレクトリの初期化
        try:
            file_utils.initialize_dirs(wiki_id)
        except FileExistsError:
            pass

        file_names = ["config.json",
                      "FrontPage.confs.json",
                      "FrontPage.histories.json",
                      "FrontPage.md",
                      "pages.json",
                      "SideBar.confs.json",
                      "SideBar.histories.json",
                      "SideBar.md",
                      "ガイダンス.confs.json",
                      "ガイダンス.histories.json",
                      "ガイダンス.md",
                      "ガイダンス_._初めてのUzuWiki.confs.json",
                      "ガイダンス_._初めてのUzuWiki.histories.json",
                      "ガイダンス_._初めてのUzuWiki.md",
                      "ガイダンス_._記法サンプル.confs.json",
                      "ガイダンス_._記法サンプル.histories.json",
                      "ガイダンス_._記法サンプル.md",
                      ]

        for file_name in file_names:
            file = render_to_string('roots/initializes/' + file_name, context)
            file_utils.put_file(wiki_id, file_name, file)

        # wiki一覧に追加
        wikis_file = file_utils.get_root_file("wikis.json")
        wikis_file = json.loads(wikis_file)

        wikis_file["data"][wiki_id] = {
            wiki_id: {
                "wiki_id": wiki_id,
                "create": timestamp,
                "update": timestamp,
                "status": "active"
            }
        }

        file_utils.put_root_file("wikis.json", json.dumps(wikis_file))

    class Meta:
        fields = ("wiki_id")
