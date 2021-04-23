import pytest
from async_generator import (
    async_generator,
    yield_,
)

from tests.utils import (
    alembic_config_from_url,
    tmp_database,
)


@pytest.fixture
@async_generator
async def empty_temp_db(prod_psql_url) -> str:
    """
    Создаем пустую временную БД
    """
    with tmp_database(db_url=prod_psql_url, suffix='pytest_migration') as tmp_url:
        await yield_(tmp_url)


@pytest.fixture
def test_db_alembic_config(empty_temp_db):
    """
    Связываем конфигурационный файл Алембика с пустой временной БД
    """
    return alembic_config_from_url(pg_url=empty_temp_db)
