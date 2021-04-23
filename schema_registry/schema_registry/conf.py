import os
from pathlib import Path

from dynaconf import LazySettings
from sqlalchemy.engine.url import URL

PROJECT_PATH = str(Path(__file__).parent.parent.resolve())

settings = LazySettings(ENVVAR_PREFIX_FOR_DYNACONF=False)


class LogConfig:
    FORMAT = settings.get(
        'LOG.format', '%(levelname)-8s# %(filename)s[LINE:%(lineno)d] [%(asctime)s.%(msecs)d]: %(message)s',
    )
    LEVEL = settings.get('LOG.level', 'INFO')


try:
    with open(os.path.join(PROJECT_PATH, '.commit'), 'r') as f:
        VERSION = f.readline().rstrip('\n')
        BRANCH = f.readline().rstrip('\n')
        COMMIT = f.readline().rstrip('\n')
except FileNotFoundError:
    VERSION = ''
    COMMIT = ''
    BRANCH = ''

_DB_DSN_KW = {
    'username': settings.POSTGRES.user,
    'password': settings.POSTGRES.password,
    'host': settings.POSTGRES.host,
    'port': settings.POSTGRES.port,
    'database': settings.POSTGRES.database,
}

DB_HOST = settings.POSTGRES.host
DB_PORT = settings.POSTGRES.port
DB_USER = settings.POSTGRES.user
DB_NAME = settings.POSTGRES.database
DB_PASSWORD = settings.POSTGRES.password

# для управления скриптом БД database.sh
BACKUP_DB = 'true' if settings.DATABASE_SCRIPT.backup_db else 'false'
DROP_DB = 'true' if settings.DATABASE_SCRIPT.drop_db else 'false'
USE_ALEMBIC = 'true' if settings.DATABASE_SCRIPT.use_alembic else 'false'
CREATE_POSTGIS = 'true' if settings.DATABASE_SCRIPT.create_postgis else 'false'

# str for alembic & test with postgresql driver
settings.DB_DSN_ALEMBIC = DSN_STR = URL(
    drivername='postgresql',
    **_DB_DSN_KW,
)

settings.DB_DSN = URL(
    drivername=settings.POSTGRES.driver,
    **_DB_DSN_KW,
)

settings.logging_params = {
    'version': 1,
    'formatters': {
        'default': {
            'format': LogConfig.FORMAT,
        },
    },
    'handlers': {
        'console': {
            'level': LogConfig.LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        'default': {
            'level': 'DEBUG',
            'handlers': ['console', 'error'],
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'error'],
    },
    'disable_existing_loggers': False,
}
