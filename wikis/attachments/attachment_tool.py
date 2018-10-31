from logging import getLogger
from commons import file_name_tools
from commons.file import file_utils
import json

logger = getLogger(__name__)


def get_or_new(wiki_id, file_name):
    """
    コメントを階層構造で取得する。
    :param wiki_id:
    :param file_name:
    :return:
    """

    logger.debug("get_or_new:start")

    try:
        comment_data = file_utils.get_file(wiki_id, file_name + ".attachments.json")
        comment_data = json.loads(comment_data)

        logger.debug("get_or_new:end")

        return comment_data

    except FileNotFoundError:

        logger.debug("comment file not found")

        new_comment_data = {
            "file_type": "attachment",
            "attachments": [],
        }

        logger.debug("get_or_new:end")

        return new_comment_data


def get_attachment_list(wiki_id, file_name):
    # 添付ファイル一覧を取得
    attachment_file_data = get_or_new(wiki_id, file_name)

    return attachment_file_data["attachments"]
