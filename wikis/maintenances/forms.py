import os
import json
from datetime import datetime
from django import forms
from commons.file import file_utils
from commons import wiki_conf_consts
from commons import page_conf_consts
from commons import file_name_tools
from logging import getLogger

logger = getLogger(__name__)


class WikiConfForm(forms.Form):
    wiki_id = forms.CharField(label='wikiID')
    name = forms.CharField(label='wiki名')
    comment_mode = forms.ChoiceField(label='コメント',
                                     widget=forms.RadioSelect,
                                     choices=sorted(wiki_conf_consts.COMMENT_MODE, key=lambda x: x[0]),
                                     initial=0)
    edit_authority = forms.ChoiceField(label='編集権限',
                                       widget=forms.RadioSelect,
                                       choices=sorted(wiki_conf_consts.EDIT_AUTHORITY, key=lambda x: x[0]),
                                       initial=0)
    release_status = forms.ChoiceField(label='公開状態',
                                       widget=forms.RadioSelect,
                                       choices=sorted(wiki_conf_consts.RELEASE_STATUS, key=lambda x: x[0]),
                                       initial=0)

    def __init__(self, wiki_id, **kwargs):
        super().__init__(**kwargs)

        wiki_conf = json.loads(file_utils.get_file(wiki_id, "config.json"))

        self.fields['wiki_id'].initial = wiki_id
        self.fields['name'].initial = wiki_conf["name"]

        confs = wiki_conf["confs"]
        self.fields['comment_mode'].initial = confs.get("comment_mode") \
            if "comment_mode" in confs else self.fields['comment_mode'].initial
        self.fields['edit_authority'].initial = confs.get("edit_authority") \
            if "edit_authority" in confs else self.fields['edit_authority'].initial
        self.fields['release_status'].initial = confs.get("release_status") \
            if "release_status" in confs else self.fields['release_status'].initial

    def put(self):
        # wikiID
        wiki_id = self.data["wiki_id"]

        # confファイル取得
        wiki_conf = json.loads(file_utils.get_file(wiki_id, "config.json"))

        wiki_conf["name"] = self.data["name"]
        wiki_conf["confs"]['comment_mode'] = self.data["comment_mode"]
        wiki_conf["confs"]['edit_authority'] = self.data["edit_authority"]
        wiki_conf["confs"]['release_status'] = self.data["release_status"]
        wiki_conf["updated_at"] = datetime.now().isoformat()

        file_utils.put_file(wiki_id, "config.json", json.dumps(wiki_conf))

    class Meta:
        fields = ("wiki_id", "name", "comment_mode", "edit_authority", "release_status")


class PageConfForm(forms.Form):
    wiki_id = forms.CharField(label='wikiID')
    page_name = forms.CharField(label='ページ名')
    comment_mode = forms.ChoiceField(label='コメント',
                                     widget=forms.RadioSelect,
                                     choices=sorted(page_conf_consts.COMMENT_MODE, key=lambda x: x[0]),
                                     initial=0)
    attachment_mode = forms.ChoiceField(label='ファイル添付',
                                        widget=forms.RadioSelect,
                                        choices=sorted(page_conf_consts.ATTACHMENT_MODE, key=lambda x: x[0]),
                                        initial=0)
    freeze_mode = forms.ChoiceField(label='凍結',
                                    widget=forms.RadioSelect,
                                    choices=sorted(page_conf_consts.FREEZE_MODE, key=lambda x: x[0]),
                                    initial=0)

    def __init__(self, wiki_id, page_dirs, **kwargs):
        super().__init__(**kwargs)

        file_name = file_name_tools.page_dirs_to_file_name(page_dirs) + ".confs.json"

        page_conf_file = file_utils.get_file(wiki_id, file_name)
        page_conf = json.loads(page_conf_file)

        self.fields['wiki_id'].initial = wiki_id
        self.fields['page_name'].initial = file_name_tools.page_dirs_to_page_name(page_dirs)

        confs = page_conf["confs"]
        self.fields['comment_mode'].initial = confs.get("comment_mode") \
            if "comment_mode" in confs else self.fields['comment_mode'].initial
        self.fields['attachment_mode'].initial = confs.get("attachment_mode") \
            if "attachment_mode" in confs else self.fields['attachment_mode'].initial
        self.fields['freeze_mode'].initial = confs.get("freeze_mode") \
            if "freeze_mode" in confs else self.fields['freeze_mode'].initial

    def put(self):
        # wikiID
        wiki_id = self.data["wiki_id"]

        file_name = file_name_tools.page_name_to_file_name(self.data["page_name"]) + ".confs.json"

        # confファイル取得
        page_conf_file = file_utils.get_file(wiki_id, file_name)
        page_conf = json.loads(page_conf_file)

        page_conf["confs"]['comment_mode'] = self.data["comment_mode"]
        page_conf["confs"]['attachment_mode'] = self.data["attachment_mode"]
        page_conf["confs"]['freeze_mode'] = self.data["freeze_mode"]
        page_conf["updated_at"] = datetime.now().isoformat()

        file_utils.put_file(wiki_id, file_name, json.dumps(page_conf))

    class Meta:
        fields = ("wiki_id", "page_name", "comment_mode", "attachment_mode", "freeze_mode")
