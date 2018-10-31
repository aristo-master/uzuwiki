import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s a',
        },
        # プロジェクト用のフォーマットを追加
        'heibon': {
            'format': '\t'.join([
                "[%(levelname)s]",
                "%(asctime)s",
                "%(name)s:%(lineno)d",
                "%(message)s",
                "%(threadName)s",
            ])
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'heibon'  # フォーマッター追加
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": [
            "console"
        ]
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'MARKDOWN': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'botocore': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'googleapiclient.discovery_cache': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    }
}
