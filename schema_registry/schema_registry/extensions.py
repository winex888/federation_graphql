import logging

from schema_registry.api.models import db
from schema_registry.conf import settings


async def init_db(_app) -> None:
    """
    Инициализация подключения к бд
    """
    logging.info('Подключение к БД... ({db_dsn})'.format(db_dsn=settings.DB_DSN))
    await db.set_bind(
        settings.DB_DSN,
        echo=settings.POSTGRES.echo,
        min_size=settings.POSTGRES.pool_min_size,
        max_size=settings.POSTGRES.pool_max_size,
        ssl=settings.POSTGRES.ssl,
    )
    try:
        await db.scalar('select now()')
        logging.info('Подключение к БД прошло успешно')
    except ConnectionRefusedError as ex:
        logging.error(
            'Ошибка подключение к БД... ({db_dsn}), ошибка: {errors}'.format(
                db_dsn=settings.DB_DSN,
                errors=ex.strerror,
            ),
        )


async def close_db(_app) -> None:
    """
    Отключение подключения к бд
    """
    logging.info('Отключение подключения к базе дынных...')
    await db.pop_bind().close()
