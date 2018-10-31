import os
import shutil
from commons.file.backends import file_balancer
from uzuwiki.settings_file_engine import COMMONS_FILE_DIR, CONFS_FILE_DIR, PAGES_FILE_DIR, ROOTS_FILE_DIR, \
    COMMONS_HISTRIES_FILE_DIR, CONFS_HISTRIES_FILE_DIR, PAGES_HISTRIES_FILE_DIR
from logging import getLogger

logger = getLogger(__name__)


def initialize_dirs(wiki_id):
    os.makedirs(os.path.join(COMMONS_FILE_DIR, wiki_id).encode())
    os.makedirs(os.path.join(CONFS_FILE_DIR, wiki_id).encode())
    os.makedirs(os.path.join(PAGES_FILE_DIR, wiki_id).encode())
    os.makedirs(os.path.join(COMMONS_HISTRIES_FILE_DIR, wiki_id).encode())
    os.makedirs(os.path.join(CONFS_HISTRIES_FILE_DIR, wiki_id).encode())
    os.makedirs(os.path.join(PAGES_HISTRIES_FILE_DIR, wiki_id).encode())


def get_root_file(file_name):
    logger.debug("get_root_file:start")

    file_path = os.path.join(ROOTS_FILE_DIR, file_name).encode()

    logger.info("ファイルを取得します。file_path=%s", file_path)

    with open(file_path, encoding="utf-8") as f:
        logger.debug("get_root_file:end")
        return f.read()


def put_root_file(file_name, file_data):
    logger.debug("put_root_file:start")

    file_path = os.path.join(ROOTS_FILE_DIR, file_name).encode()
    logger.info("ファイルを保存します。file_path=%s", file_path)

    with open(file_path, mode='w', encoding="utf-8") as f:
        # 改行コードをLFに統一する。
        f.write(file_data.replace('\r', ''))

    logger.debug("put_root_file:end")


def get_file(wiki_id, file_name):
    logger.debug("get_page_file_data:start")

    target_dir = file_balancer.get_target(file_name)

    if target_dir == file_balancer.commons:
        dir = COMMONS_FILE_DIR
    elif target_dir == file_balancer.confs:
        dir = CONFS_FILE_DIR
    else:
        dir = PAGES_FILE_DIR

    file_path = os.path.join(dir, wiki_id, file_name).encode()

    logger.info("ファイルを取得します。file_path=%s", file_path)

    with open(file_path, encoding="utf-8") as f:
        logger.debug("get_page_file:end")
        return f.read()


def put_file(wiki_id, file_name, page_data):
    logger.debug("put_page_file:start")

    target_dir = file_balancer.get_target(file_name)

    if target_dir == file_balancer.commons:
        dir = COMMONS_FILE_DIR
    elif target_dir == file_balancer.confs:
        dir = CONFS_FILE_DIR
    else:
        dir = PAGES_FILE_DIR

    file_path = os.path.join(dir, wiki_id, file_name).encode()
    logger.info("ファイルを保存します。file_path=%s", file_path)

    with open(file_path, mode='w', encoding="utf-8") as f:
        # 改行コードをLFに統一する。
        f.write(page_data.replace('\r', ''))

    logger.debug("put_page_file:end")


def get_history_file(wiki_id, file_name):
    logger.debug("get_page_file_data:start")

    target_dir = file_balancer.get_target(file_name)

    if target_dir == file_balancer.commons:
        dir = COMMONS_HISTRIES_FILE_DIR
    elif target_dir == file_balancer.confs:
        dir = CONFS_HISTRIES_FILE_DIR
    else:
        dir = PAGES_HISTRIES_FILE_DIR

    file_path = os.path.join(dir, wiki_id, file_name).encode()

    logger.info("ファイルを取得します。file_path=%s", file_path)

    with open(file_path, encoding="utf-8") as f:
        logger.debug("get_page_file:end")
        return f.read()


def put_history(wiki_id, file_name, backup_file_name):
    logger.debug("back_up_file:start")

    target_dir = file_balancer.get_target(file_name)

    if target_dir == file_balancer.commons:
        dir = COMMONS_FILE_DIR
        his_dir = COMMONS_HISTRIES_FILE_DIR
    elif target_dir == file_balancer.confs:
        dir = CONFS_FILE_DIR
        his_dir = CONFS_HISTRIES_FILE_DIR
    else:
        dir = PAGES_FILE_DIR
        his_dir = PAGES_HISTRIES_FILE_DIR

    file_path = os.path.join(dir, wiki_id, file_name).encode()
    backup_file_path = os.path.join(his_dir, wiki_id, backup_file_name).encode()

    logger.info("ファイルをバックアップします。file_path=%s", backup_file_path)

    shutil.copy2(file_path, backup_file_path)

    logger.debug("back_up_file:end")


from commons.file.backends import file_engine_s3


def put_static_file(wiki_id, file_name, file_data):
    path = os.path.join(STATIC_FILE_DIR, wiki_id, file_name)

    logger.info("添付ファイルを保存します。file_path=%s", path)
    destination = open(path, 'wb')

    for chunk in file_data.chunks():
        destination.write(chunk)

    destination.close()

    file_engine_s3.put_static_file(wiki_id, file_name, file_data)

    return path[len(STATIC_FILE_DIR):]
