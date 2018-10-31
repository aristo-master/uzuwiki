from importlib import import_module
from commons.file.backends.static_file_engines import static_file_engines
from uzuwiki import settings_file_engine
from uzuwiki import settings_static_file_engine


def initialize_dirs(wiki_id):
    engine = import_module(settings_file_engine.FILE_ENGINE)
    engine.initialize_dirs(wiki_id)

    engine = import_module(settings_static_file_engine.STATIC_FILE_ENGINE)
    return engine.initialize_dirs(wiki_id)


def get_root_file(file_name):
    engine = import_module(settings_file_engine.FILE_ENGINE)
    return engine.get_root_file(file_name)


def put_root_file(file_name, file_data):
    engine = import_module(settings_file_engine.FILE_ENGINE)
    return engine.put_root_file(file_name, file_data)


def get_file(wiki_id, file_name):
    engine = import_module(settings_file_engine.FILE_ENGINE)
    return engine.get_file(wiki_id, file_name)


def put_file(wiki_id, file_name, page_data):
    engine = import_module(settings_file_engine.FILE_ENGINE)
    return engine.put_file(wiki_id, file_name, page_data)


def get_history_file(wiki_id, file_name):
    engine = import_module(settings_file_engine.FILE_ENGINE)
    return engine.get_history_file(wiki_id, file_name)


def put_history(wiki_id, file_name, backup_file_name):
    engine = import_module(settings_file_engine.FILE_ENGINE)
    return engine.put_history(wiki_id, file_name, backup_file_name)


def put_static_file(wiki_id, file_name, file_data):
    engine = import_module(settings_static_file_engine.STATIC_FILE_ENGINE)
    return engine.put_static_file(wiki_id, file_name, file_data)


def get_static_file_url(attachment_record):
    engine = import_module(static_file_engines[attachment_record["type"]])
    return engine.get_static_file_url(attachment_record)
