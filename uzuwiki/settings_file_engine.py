import os
from uzuwiki.settings import BASE_DIR, STATICFILES_DIRS

#######################################################################################
# UzuWikiは、Wikiのページデータや設定をファイル形式で保持しています。
# ファイルの保存先となるストレージは「ローカルディスク」と「Amazon S3」に対応しています。
#######################################################################################

#############################
# ファイルエンジンの設定
# ローカルディスクエンジンか、Amazon S3エンジンのいずれか一方を選択して下さい。
##############
# ローカルディスクエンジン
FILE_ENGINE = 'commons.file.backends.file_engine_local'
# Amazon S3エンジン
# FILE_ENGINE = 'commons.file.backends.file_engine_s3'

#############################
# ローカルディスクエンジンで必要な設定
##############
FILE_BASE_DIR = BASE_DIR
COMMONS_FILE_DIR = os.path.join(FILE_BASE_DIR, "_data", "commons")
CONFS_FILE_DIR = os.path.join(FILE_BASE_DIR, "_data", "confs")
PAGES_FILE_DIR = os.path.join(FILE_BASE_DIR, "_data", "pages")
ROOTS_FILE_DIR = os.path.join(FILE_BASE_DIR, "_data", "roots")
COMMONS_HISTRIES_FILE_DIR = os.path.join(FILE_BASE_DIR, "_data", "histories", "commons")
CONFS_HISTRIES_FILE_DIR = os.path.join(FILE_BASE_DIR, "_data", "histories", "confs")
PAGES_HISTRIES_FILE_DIR = os.path.join(FILE_BASE_DIR, "_data", "histories", "pages")

#############################
# Amazon S3エンジンで必要な設定
##############
BUGGET_NAME = "uzuwiki-doc"
STATIC_BUGGET_NAME = "uzuwiki-static"
COMMONS_FILE_S3_PATH = {"bugget_name": BUGGET_NAME, "path": "commons"}
CONFS_FILE_S3_PATH = {"bugget_name": BUGGET_NAME, "path": "confs"}
PAGES_FILE_S3_PATH = {"bugget_name": BUGGET_NAME, "path": "pages"}
ROOTS_FILE_S3_PATH = {"bugget_name": BUGGET_NAME, "path": "roots"}
COMMONS_HISTRIES_FILE_S3_PATH = {"bugget_name": BUGGET_NAME, "path": "/".join(["histories", "commons"])}
CONFS_HISTRIES_FILE_S3_PATH = {"bugget_name": BUGGET_NAME, "path": "/".join(["histories", "confs"])}
PAGES_HISTRIES_FILE_S3_PATH = {"bugget_name": BUGGET_NAME, "path": "/".join(["histories", "pages"])}

# １ページ辺りの最大サイズ（256KB）
MAX_PAGE_SIZE = 256 * 1024
MAX_PAGE_SIZE_MESSAGE = "ページのサイズが大きすぎます。ページを分割するなどして１ページのサイズを小さくして下さい。"
