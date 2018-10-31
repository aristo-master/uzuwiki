from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from commons.file import file_utils
from uzuwiki.settings_static_file_engine import *
import tempfile
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from commons.errors import GoogleCredentialsError
import httplib2
import os
import hashlib
import oauth2client
from datetime import datetime
import mimetypes
from logging import getLogger

logger = getLogger(__name__)


def initialize_dirs(wiki_id):
    pass


def _get_drive(temp):
    try:
        credentials_file = file_utils.get_root_file('credentials.json')
    except FileNotFoundError as e:
        raise GoogleCredentialsError('credentialsが見つかりません。管理人は初期認証を行ってください。')

    try:
        os.makedirs(temp.name)
    except FileExistsError:
        pass

    credentials_path = os.path.join(temp.name, 'credentials.json')

    # ダウンロードしたcredentialsを一時領域に保存
    with open(credentials_path, mode='w') as f:
        f.write(credentials_file)

    logger.debug("credentials_path=%s", credentials_path)

    storage = Storage(credentials_path)
    credentials = storage.get()
    if not credentials or credentials.invalid:

        logger.debug("credentials.invalid")

        try:
            http = httplib2.Http(timeout=None)
            credentials.refresh(http)

            # リフレッシュしたcredentialsを保存
            storage = Storage(credentials_path)
            storage.put(credentials)

            with open(credentials_path, encoding="utf-8") as f:
                file_utils.put_root_file('credentials.json', f.read())

        except AccessTokenRefreshError as error:
            raise GoogleCredentialsError("アクセストークンのリフレッシュに失敗しました。管理人は認証を行ってください。")

    else:
        logger.debug("credentials.valid")

    gauth = GoogleAuth()
    gauth.settings["client_config_backend"] = "settings"
    gauth.settings["client_config"] = {}
    gauth.settings["client_config"]["client_id"] = GOOGLE_CREDENTIALS_CLIENT_ID
    gauth.settings["client_config"]["client_secret"] = GOOGLE_CREDENTIALS_CLIENT_SECRET
    gauth.settings["client_config"]["auth_uri"] = oauth2client.GOOGLE_AUTH_URI
    gauth.settings["client_config"]["token_uri"] = oauth2client.GOOGLE_TOKEN_URI
    gauth.settings["client_config"]["revoke_uri"] = oauth2client.GOOGLE_REVOKE_URI
    gauth.settings["client_config"]["redirect_uri"] = ""
    gauth.LoadCredentialsFile(credentials_file=credentials_path)

    drive = GoogleDrive(gauth)

    return drive


def put_static_file(wiki_id, file_name, file_data):
    logger.debug("put_static_file:start")

    temp = tempfile.TemporaryDirectory()

    drive = _get_drive(temp)

    # ファイルを一時領域に保存
    attach_file_path = os.path.join(temp.name, file_name)

    destination = open(attach_file_path, 'wb')

    for chunk in file_data.chunks():
        destination.write(chunk)

    destination.close()

    base_name, ext = os.path.splitext(file_name)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    digest_file_name = hashlib.md5((base_name + timestamp).encode("UTF-8")).hexdigest()

    title = "/".join([wiki_id, digest_file_name + ext])
    file1 = drive.CreateFile({'title': title,
                              "parents": [
                                  {"kind": "drive#fileLink",
                                   "id": GOOGLE_STATIC_FOLDER_ID
                                   }
                              ]})

    file1.SetContentFile(attach_file_path)

    logger.info("Googleドライブに保存します。title=%s", title)
    file1.Upload()

    logger.debug("アップロード完了")
    param = "'{}' in parents and trashed=false".format(GOOGLE_STATIC_FOLDER_ID)
    file_list = drive.ListFile({'q': param}).GetList()

    file_id = None
    for file1 in file_list:
        # logger.debug('title: %s, id: %s' % (file1['title'], file1['id']))
        if file1['title'] == title:
            file_id = file1['id']

    if not file_id:
        raise Exception("アップロードファイルのIDを取得出来ませんでした。")

    mime = mimetypes.guess_type(attach_file_path)

    record = {
        "type": "google",
        "id": file_id,
        "name": file_name,
        "mime": mime[0],
        "size": os.path.getsize(attach_file_path),
        "path": title,
        "folder": GOOGLE_STATIC_FOLDER_ID,
        "timestamp": datetime.now().isoformat(),
    }

    logger.debug("record=%s", record)

    return record


def get_static_file_url(attachment_record):
    url = "http://drive.google.com/uc?export=view&id={}"
    return url.format(attachment_record["id"])
