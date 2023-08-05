import logging.config


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "%(asctime)s %(levelname)s %(name)s: %(message)s",
            'datefmt': '%H:%M:%S'
        },
        'api_call': {
            'format': (
                '%(asctime)s [%(levelname)s] %(message)s in %(pathname)s `%(funcName)s`: '),
            'datefmt': '%H:%M:%S'
        }
    },
    'handlers': {
        'default': {'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'},
        'api_call': {'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'api_call'},
    },
    'loggers': {
        'asamended.uscode.client': {
            'handlers': ['api_call'], 'level': 'INFO', 'propagate': False
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)