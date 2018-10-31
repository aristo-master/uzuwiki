import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#######################################################################################
# 添付ファイル用のエンジン
# 画像や圧縮ファイルのアップロードを可能とする添付ファイルは、
# ページのドキュメントと比べると一つ辺りのデータ量が巨大になる可能性があります。
# そこで、UzuWikiでは添付ファイルの保存先をドキュメントとは切り分けて管理することが出来ます。
# 添付ファイルエンジンは以下を用意しています。
#
# １．ローカルディスクエンジン
#   　オンプレミス環境において、同じサーバ内に添付ファイルを設置します。
#   　・アクセス殺到時にサーバが重くなる可能性があります。
#   　・アクセス殺到時に伝送量が圧迫される可能性があります。
#     ・負荷の心配がある場合、ディスクスペースを分割するなどの対策を検討して下さい。
# ２．Amazon S3エンジン
#     Amazon S3に添付ファイルを設置します。
#     ・ドキュメント本体とは別のバゲットを設定することをお薦めします。
#     ・添付ファイル用のバゲットは公開設定にする必要があります。
# 　　　このため、Wikiを介さず直接アクセスが可能となります。
#     ・アクセス殺到時に伝送量が増大する可能性があります。
# ３．Googleドライブエンジン
#     Googleドライブ：Googleドライブに添付ファイルを設置します。
#     アクセス殺到時の負荷、伝送コスト増大の心配がありません。
#     ただし、Googleドライブの規約は個人利用のみ。商用利用が禁止になっています。
#     個人利用の範囲を超える場合はG Suiteを契約してください。
#     https://www.google.com/intl/ja_ALL/drive/terms-of-service/
#######################################################################################

#############################
# ファイルエンジンの設定
# いずれか一方を選択して下さい。
##############
# ローカルディスクエンジン
STATIC_FILE_ENGINE = 'commons.file.backends.static_file_engine_local'
# Amazon S3エンジン
# STATIC_FILE_ENGINE = 'commons.file.backends.static_file_engine_s3'
# Google ドライブエンジン
# STATIC_FILE_ENGINE = 'commons.file.backends.static_file_engine_google'

#############################
# ローカルディスクエンジンで必要な設定
##############
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "_static"),
)
STATIC_FILE_DIR = STATICFILES_DIRS[0]

#############################
# Amazon S3エンジンで必要な設定
##############
# STATIC_URL = 'https://s3-ap-northeast-1.amazonaws.com/uzuwiki-static/static/'
STATIC_BUGGET_NAME = "uzuwiki-static"
STATIC_FILE_S3_PATH = {"bugget_name": STATIC_BUGGET_NAME, "path": "static"}

#############################
# Googleドライブエンジンで必要な設定
##############
GOOGLE_CREDENTIALS_CLIENT_ID = os.environ.get('GOOGLE_CREDENTIALS_CLIENT_ID')
GOOGLE_CREDENTIALS_CLIENT_SECRET = os.environ.get('GOOGLE_CREDENTIALS_CLIENT_SECRET')
GOOGLE_STATIC_FOLDER_ID = os.environ.get('GOOGLE_STATIC_FOLDER_ID')

# 添付ファイルの最大サイズ（１ＭＢ）
MAX_FILE_SIZE = 1024 * 1024
MAX_FILE_SIZE_MESSAGE = "添付ファイルのサイズは1MB未満にして下さい。"
