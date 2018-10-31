import botocore
import boto3
from commons.file.backends import file_balancer
from uzuwiki.settings_file_engine import *
from logging import getLogger

logger = getLogger(__name__)


def _put_s3(bugget_name, path, body, public_flg=False):
    s3 = boto3.resource('s3')
    obj = s3.Object(bugget_name, path)

    logger.info("ファイルを保存します。bugget_name=%s,path=", bugget_name, path)

    if public_flg:
        obj.put(Body=body, ACL='public-read')
    else:
        obj.put(Body=body)


def _get_s3(bugget_name, path):
    s3 = boto3.resource('s3')
    obj = s3.Object(bugget_name, path)

    logger.info("ファイルを取得します。bugget_name=%s / path=%s", bugget_name, path)

    try:
        file = obj.get()['Body'].read().decode('utf-8')
        return file

    except botocore.exceptions.NoCredentialsError as e:

        raise e

    except Exception as e:

        if e.response['Error']['Code'] == "NoSuchKey":
            logger.warning("ファイルが存在しません。bugget_name=%s / path=%s", bugget_name, path)
            raise FileNotFoundError()
        else:
            raise e


def initialize_dirs(wiki_id):
    _put_s3(COMMONS_FILE_S3_PATH["bugget_name"], "/".join([COMMONS_FILE_S3_PATH["path"], wiki_id, "init"]), "")
    _put_s3(CONFS_FILE_S3_PATH["bugget_name"], "/".join([CONFS_FILE_S3_PATH["path"], wiki_id, "init"]), "")
    _put_s3(PAGES_FILE_S3_PATH["bugget_name"], "/".join([PAGES_FILE_S3_PATH["path"], wiki_id, "init"]), "")
    _put_s3(COMMONS_HISTRIES_FILE_S3_PATH["bugget_name"],
            "/".join([COMMONS_HISTRIES_FILE_S3_PATH["path"], wiki_id, "init"]), "")
    _put_s3(CONFS_HISTRIES_FILE_S3_PATH["bugget_name"],
            "/".join([CONFS_HISTRIES_FILE_S3_PATH["path"], wiki_id, "init"]), "")
    _put_s3(PAGES_HISTRIES_FILE_S3_PATH["bugget_name"],
            "/".join([PAGES_HISTRIES_FILE_S3_PATH["path"], wiki_id, "init"]), "")


def get_root_file(file_name):
    logger.debug("get_root_file:start")

    file = _get_s3(ROOTS_FILE_S3_PATH["bugget_name"], "/".join([ROOTS_FILE_S3_PATH["path"], file_name]))

    logger.debug("get_root_file:end")

    return file


def put_root_file(file_name, file_data):
    logger.debug("put_root_file:start")

    _put_s3(ROOTS_FILE_S3_PATH["bugget_name"], "/".join([ROOTS_FILE_S3_PATH["path"], file_name]), file_data)

    logger.debug("put_root_file:end")


def get_file(wiki_id, file_name):
    logger.debug("get_page_file_data:start")

    target_S3_PATH = file_balancer.get_target(file_name)

    if target_S3_PATH == file_balancer.commons:
        dir = COMMONS_FILE_S3_PATH
    elif target_S3_PATH == file_balancer.confs:
        dir = CONFS_FILE_S3_PATH
    else:
        dir = PAGES_FILE_S3_PATH

    file = _get_s3(dir["bugget_name"], "/".join([dir["path"], wiki_id, file_name]))

    logger.debug("get_page_file_data:end")

    return file


def put_file(wiki_id, file_name, page_data):
    logger.debug("put_page_file:start")

    target_S3_PATH = file_balancer.get_target(file_name)

    if target_S3_PATH == file_balancer.commons:
        dir = COMMONS_FILE_S3_PATH
    elif target_S3_PATH == file_balancer.confs:
        dir = CONFS_FILE_S3_PATH
    else:
        dir = PAGES_FILE_S3_PATH

    _put_s3(dir["bugget_name"], "/".join([dir["path"], wiki_id, file_name]), page_data)

    logger.debug("put_page_file:end")


def get_history_file(wiki_id, file_name):
    logger.debug("get_page_file_data:start")

    target_S3_PATH = file_balancer.get_target(file_name)

    if target_S3_PATH == file_balancer.commons:
        dir = COMMONS_HISTRIES_FILE_S3_PATH
    elif target_S3_PATH == file_balancer.confs:
        dir = CONFS_HISTRIES_FILE_S3_PATH
    else:
        dir = PAGES_HISTRIES_FILE_S3_PATH

    file = _get_s3(dir["bugget_name"], "/".join([dir["path"], wiki_id, file_name]))

    return file


def put_history(wiki_id, file_name, backup_file_name):
    logger.debug("back_up_file:start")

    target_S3_PATH = file_balancer.get_target(file_name)

    if target_S3_PATH == file_balancer.commons:
        dir = COMMONS_FILE_S3_PATH
        his_S3_PATH = COMMONS_HISTRIES_FILE_S3_PATH
    elif target_S3_PATH == file_balancer.confs:
        dir = CONFS_FILE_S3_PATH
        his_S3_PATH = CONFS_HISTRIES_FILE_S3_PATH
    else:
        dir = PAGES_FILE_S3_PATH
        his_S3_PATH = PAGES_HISTRIES_FILE_S3_PATH

    file_path = "/".join([dir["path"], wiki_id, file_name])
    backup_file_path = "/".join([his_S3_PATH["path"], wiki_id, backup_file_name])

    back_up_file = _get_s3(dir["bugget_name"], file_path)
    _put_s3(dir["bugget_name"], backup_file_path, back_up_file)

    logger.debug("back_up_file:end")
