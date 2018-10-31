from django.conf import settings
from importlib import import_module

SETTING_PREFIX = 'SOCIAL_AUTH'


def to_setting_name(*names):
    return '_'.join([name.upper().replace('-', '_') for name in names if name])


def setting_name(*names):
    return to_setting_name(*((SETTING_PREFIX,) + names))


STRATEGY = getattr(settings, setting_name('STRATEGY'),
                   'social_django.strategy.DjangoStrategy')
STORAGE = getattr(settings, setting_name('STORAGE'),
                  'social_django.models.DjangoStorage')


def get_strategy(strategy, storage, *args, **kwargs):
    Strategy = module_member(strategy)
    Storage = module_member(storage)
    return Strategy(Storage, *args, **kwargs)


def module_member(name):
    mod, member = name.rsplit('.', 1)
    module = import_module(mod)
    return getattr(module, member)


def load_strategy(request=None):
    return get_strategy(STRATEGY, STORAGE, request)
