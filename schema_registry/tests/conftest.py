import graphene
import pytest
from alembic.command import upgrade
from async_generator import (
    async_generator,
    yield_,
)
from graphene.test import Client
from mock import Mock
from yarl import URL

from schema_registry.api.schema import (
    Mutation,
    Query,
)
from schema_registry.conf import (
    DSN_STR,
    settings,
)
from tests.utils import (
    alembic_config_from_url,
    tmp_database,
)


@pytest.fixture(scope='session', autouse=True)
def set_test_settings():
    """
    Явно задаем тестовое окружение для dynaconf
    """
    settings.configure(FORCE_ENV_FOR_DYNACONF='testing')


@pytest.fixture(scope='session')
def prod_psql_url() -> URL:
    """
    Базовый postgresql URL боевой БД
    """
    pg_url = URL(str(DSN_STR))
    return pg_url


@pytest.fixture
def graphene_client():
    """
    graphene клиент для имитации запросов к schema
    Для работы необходимо добавить фикстуру requests
    """
    schema = graphene.Schema(
        query=Query,
        auto_camelcase=False,
        mutation=Mutation,
    )
    return Client(schema, return_promise=True)


@pytest.fixture
async def requests(migrated_temp_db):
    """
    Добавляет необходимые ресурсы в имитацию запросов от graphene.test клиента
    """
    request = Mock()
    return {'request': request}


@pytest.fixture(scope='session')
@async_generator
async def migrated_temp_db_template(prod_psql_url):
    """
    Создаем пустую временную БД и применяем миграции.
    Созданная БД используется как шаблон для быстрого пересоздания БД для тестов
    """
    with tmp_database(db_url=prod_psql_url, suffix='migrated_template') as tmp_url:
        alembic_config = alembic_config_from_url(pg_url=tmp_url)
        upgrade(alembic_config, 'head')
        await yield_(tmp_url)


@pytest.fixture
@async_generator
async def migrated_temp_db(prod_psql_url, migrated_temp_db_template):
    """
    Копируем чистую БД с миграциями, используя шаблон БД.
    Фикстура используется для тестов, где необходима чистая БД с миграциями
    """
    template_db_name = URL(migrated_temp_db_template).name
    with tmp_database(db_url=prod_psql_url, suffix='pytest_api', template=template_db_name) as tmp_url:
        await yield_(tmp_url)
