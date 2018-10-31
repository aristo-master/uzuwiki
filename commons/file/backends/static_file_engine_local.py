import os
from uzuwiki.settings_static_file_engine import STATIC_FILE_DIR
from uzuwiki.settings import STATIC_URL, STATIC_URL
import hashlib
from datetime import datetime
import mimetypes
from logging import getLogger

logger = getLogger(__name__)


def initialize_dirs(wiki_id):
    os.makedirs(os.path.join(STATIC_FILE_DIR, wiki_id).encode())


def put_static_file(wiki_id, file_name, file_data):
    logger.debug("put_static_file:start")

    base_name, ext = os.path.splitext(file_name)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    digest_file_name = hashlib.md5((base_name + timestamp).encode("UTF-8")).hexdigest()

    path = os.path.join(STATIC_FILE_DIR, wiki_id, digest_file_name + ext)

    logger.info("添付ファイルを保存します。file_path=%s", path)
    destination = open(path, 'wb')

    for chunk in file_data.chunks():
        destination.write(chunk)

    destination.close()

    mime = mimetypes.guess_type(path)

    record = {
        "type": "local",
        "id": digest_file_name,
        "name": file_name, "mime": mime[0],
        "size": os.path.getsize(path),
        "path": path,
        "timestamp": datetime.now().isoformat(),
    }

    logger.debug("record=%s", record)

    return record


def get_static_file_url(attachment_record):
    return STATIC_URL + attachment_record["path"][len(STATIC_FILE_DIR) + 1:]
