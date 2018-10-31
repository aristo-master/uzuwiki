import re

"""
ファイルのロードバランサー。
ローカルファイルエンジン駆動の場合、一ヵ所のフォルダにアクセスが殺到すると負荷問題に発展する可能性があるため、
分散を可能にしておく。
S3ファイルエンジン駆動の場合、負荷問題が発生する可能性は低いと思われるが、
アクセスの多い特定ファイルだけバゲットを分けたいという需要が発生する可能性を考慮し、
同じく分散を可能にしておく。
"""

commons = 0
confs = 1
pages = 2
repatter_sidebar = re.compile(r"^SideBar\.md$|SideBar\.[0-9]*.md$|^SideBar\..*\.json$")


def get_target(file_name):
    if file_name == "config.json":
        return confs
    elif repatter_sidebar.match(file_name):
        return commons
    elif file_name == "pages.json":
        return commons
    else:
        return pages
