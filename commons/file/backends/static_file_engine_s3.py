from uzuwiki.settings_static_file_engine import *
from commons.file.backends.file_engine_s3 import _put_s3
from logging import getLogger
import os
import hashlib
import mimetypes
import tempfile
from datetime import datetime

logger = getLogger(__name__)


def initialize_dirs(wiki_id):
    _put_s3(STATIC_FILE_S3_PATH["bugget_name"],
            "/".join([STATIC_FILE_S3_PATH["path"], wiki_id, "init"]), "")


def put_static_file(wiki_id, file_name, file_data):
    logger.debug("put_static_file:start")

    temp = tempfile.TemporaryDirectory()

    base_name, ext = os.path.splitext(file_name)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    digest_file_name = hashlib.md5((base_name + timestamp).encode("UTF-8")).hexdigest()

    path = "/".join([STATIC_FILE_S3_PATH["path"], wiki_id, digest_file_name + ext])

    dir = STATIC_FILE_S3_PATH
    _put_s3(dir["bugget_name"], path, file_data, public_flg=True)

    # ファイルを一時領域に保存
    attach_file_path = os.path.join(temp.name, file_name)

    destination = open(attach_file_path, 'wb')

    for chunk in file_data.chunks():
        destination.write(chunk)

    destination.close()

    mime = mimetypes.guess_type(attach_file_path)

    record = {
        "type": "s3",
        "id": digest_file_name,
        "mime": mime[0],
        "size": os.path.getsize(attach_file_path),
        "name": file_name,
        "path": path[len(dir["path"]):],
        "bugget": dir["bugget_name"],
        "timestamp": datetime.now().isoformat(),
    }

    logger.debug("record=%s", record)

    logger.debug("put_static_file:end")

    return record


def get_static_file_url(attachment_record):
    return STATIC_URL + attachment_record["path"][1:]
