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
        comment_data = file_utils.get_file(wiki_id, file_name + ".comments.json")
        comment_data = json.loads(comment_data)

        logger.debug("get_or_new:end")

        return comment_data

    except FileNotFoundError:

        logger.debug("comment file not found")

        new_comment_data = {
            "file_type": "comment",
            "comments": [
            ]
        }

        logger.debug("get_or_new:end")

        return new_comment_data


def get_comments_short(wiki_id, page_name):
    logger.debug("get_comments_short:start")

    file_name = file_name_tools.page_name_to_file_name(page_name)

    try:
        comment_data = file_utils.get_file(wiki_id, file_name + ".comments.json")
        comment_data = json.loads(comment_data)

        comments = []
        for comment in reversed(comment_data["comments"]):
            comment["children"] = []
            comment["hierarchy"] = 0
            comments.append(comment)

        logger.debug("get_comments_short:end")
        return comments

    except FileNotFoundError:

        logger.debug("comment file not found")

        logger.debug("get_comments_short:end")
        # ファイルが存在しない場合は空リストを返却する。
        return []


def get_comments_hierarchy(wiki_id, page_dirs):
    """
    コメントを階層構造で取得する。
    :param wiki_id:
    :param page_dirs:
    :return:
    """
    logger.debug("get_comments_hierarchy:start")
    file_name = file_name_tools.page_dirs_to_file_name(page_dirs)

    try:
        comment_data = file_utils.get_file(wiki_id, file_name + ".comments.json")
        comment_data = json.loads(comment_data)

        comment_dict = {}

        for comment in comment_data["comments"]:
            comment["children"] = []
            comment["hierarchy"] = 0
            comment_dict["comment_" + str(comment["id"])] = comment

        comment_list_root = []
        for key in comment_dict:

            comment = comment_dict[key]

            if comment["parent"] != 0:
                comment_dict["comment_" + str(comment["parent"])]["children"].append(key)
            else:
                comment_list_root.append(comment)

        comment_list = []
        for comment in comment_list_root:
            comment_list.append(comment)

            comment_list = _recursion_children(comment_list, comment_dict, comment, 1)

        logger.debug("get_comments_hierarchy:end")
        return comment_list

    except FileNotFoundError:

        logger.debug("comment file not found")

        logger.debug("get_comments_hierarchy:end")
        # ファイルが存在しない場合は空リストを返却する。
        return []


def _recursion_children(comment_list, comment_dict, comment, hierarchy):
    for child_key in comment["children"]:
        comment_dict[child_key]["hierarchy"] = hierarchy
        comment_list.append(comment_dict[child_key])
        comment_list = _recursion_children(comment_list, comment_dict, comment_dict[child_key], hierarchy + 1)

    return comment_list
