from pathlib import Path

from dynaconf import LazySettings

PROJECT_PATH = str(Path(__file__).parent.parent.resolve())

settings = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF=False)

settings.logging_params = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'default': {'class': 'logging.StreamHandler'}},
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO' if not settings.DEBUG else 'DEBUG',
            'propagate': True,
        },
    },
}
