from logging import getLogger

logger = getLogger(__name__)

"""
用語整理
「カテゴリ１/カテゴリ２/ページ」：ページ名(page_name)。画面に表示されるページ名
「カテゴリ１_._カテゴリ２_._ページ」：ファイル名(file_name)。サーバ上に保存されるファイル名。
[カテゴリ１,カテゴリ２,ページ]：ページディレクトリ(page_dirs)。配列状態でページを特定するももの。
"""


def page_name_to_file_name(page_name):
    """
    「カテゴリ１/カテゴリ２/ページ」のように表示上のページ名の文字列を
    「カテゴリ１_._カテゴリ２_._ページ」というファイル名形式に変換する。
    :param page_name:
    :return:
    """
    # 隠し仕様
    # ページ名に「_._」が使われている場合、自動的にディレクトリ分解点として扱う。
    file_name = page_name.replace('_._', "/")
    # ページ名に「>」が使われている場合、自動的にディレクトリ分解点として扱う。
    file_name = page_name.replace('>', "/")
    page_dirs = file_name.split("/")

    return page_dirs_to_file_name(page_dirs)


def file_name_to_page_name(page_name):
    """
    「カテゴリ１_._カテゴリ２_._ページ」というファイル名形式の文字列を
    「カテゴリ１/カテゴリ２/ページ」の表示上のページ名に変換する。
    :param page_name:
    :return:
    """
    page_name = page_name.replace('_._', "/")

    return page_name


def page_dirs_to_file_name(page_dirs):
    """
    [カテゴリ１,カテゴリ２,ページ]というディレクトリの配列状態になっているページパスを
    「カテゴリ１_._カテゴリ２_._ページ」というファイル名形式に変換する。
    :param page_dirs:
    :return:
    """
    file_name = ""
    for page_dir in page_dirs:
        if page_dir:
            file_name = file_name + page_dir.strip() + '_._'

    file_name = file_name[0:-len('_._')]
    file_name = _replace_windows_ng_word(file_name)

    return file_name


def page_dirs_to_page_name(page_dirs):
    """
    [カテゴリ１,カテゴリ２,ページ]というディレクトリの配列状態になっているページパスを
    「カテゴリ１/カテゴリ２/ページ」というファイル名に変換する。
    :param page_dirs:
    :return:
    """
    page_name = ""
    for page_dir in page_dirs:
        if page_dir:
            page_name = page_name + page_dir + "/"

    page_name = page_name[0:-1]
    page_name = _replace_windows_ng_word(page_name)

    return page_name


def to_page_dirs(page_name):
    """
    「カテゴリ１/カテゴリ２/ページ」のように表示上のページ名の文字列、もしくは
    「カテゴリ１_._カテゴリ２_._ページ」というファイル名形式を、
    [カテゴリ１,カテゴリ２,ページ]というディレクトリの配列状態に変換する。
    :param page_name:
    :return:
    """
    page_name = _replace_windows_ng_word(page_name)
    page_name = page_name.replace('_._', "/")
    page_name = page_name.replace('>', "/")

    page_dirs = page_name.split("/")
    return page_dirs


def _replace_windows_ng_word(str):
    """
    隠し仕様
    Windows環境のファイル名として使用出来ない文字を全角に置換する
    :param str:
    :return:
    """
    str = str.replace('\\', "￥")
    str = str.replace(':', "：")
    str = str.replace('\"', ">")
    str = str.replace('*', "＊")
    str = str.replace('?', "？")
    str = str.replace('\"', "”")
    str = str.replace('|', "｜")
    str = str.replace('<', "＜")

    return str
