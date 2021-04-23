import logging
import re
from asyncio import gather

import aiohttp
from aiohttp import ClientConnectorError
from graphene import (
    Enum,
    Field,
    List,
    ObjectType,
    String,
)

from schema_registry.api.models import Schema as SchemaDb
from schema_registry.api.models import db
from schema_registry.conf import (
    BRANCH,
    COMMIT,
    VERSION,
    settings,
)


class StatusConnection(Enum):
    CONNECTED = 'Connected'
    DISCONNECTED = 'Disconnected'


re_host = re.compile(r'(?<=\/\/)\S*(?=:)')
re_port = re.compile(r'(?<=:)?\d*(?=(\/graphql|$))')


class Connection(ObjectType):
    name = String(description='Название подключения')
    status = Field(StatusConnection, description='Статус подключения')
    host = String(description='Хост')
    port = String(description='Порт')


class Healthcheck(ObjectType):
    branch = String(description='Название ветки')
    version = String(description='Версия')
    commit = String(description='Хэш коммита')
    service = String(description='Название сервиса')
    connections = List(Connection, description='Подключения')


async def ping_db():
    try:
        await db.scalar('select now()')
        return StatusConnection.CONNECTED
    except ConnectionRefusedError as ex:
        logging.error(msg=ex.strerror)
        return StatusConnection.DISCONNECTED


async def ping_redis(conn):
    try:
        await conn.execute('ping')
        return StatusConnection.CONNECTED
    except ConnectionRefusedError as ex:
        logging.error(msg=ex.strerror)
        return StatusConnection.DISCONNECTED


def parse_graphql_url(url):
    return {
        'host': re_host.search(url).group(0),
        'port': re_port.search(url).group(0),
    }


async def ping_service(protocol, host, port, endpoint, name, url=None):
    url = '{protocol}://{host}:{port}/{endpoint}'.format(
        protocol=protocol,
        host=host,
        port=port,
        endpoint=endpoint,
    ) if not url else url
    connection = Connection(
        name=name,
        **parse_graphql_url(url),
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                await resp.text()
        connection.status = StatusConnection.CONNECTED
    except ClientConnectorError as ex:
        logging.error(msg=ex)
        connection.status = StatusConnection.DISCONNECTED
    return connection


class HealthcheckQuery(ObjectType):
    schema_registry_healthcheck = Field(Healthcheck)

    @classmethod
    async def resolve_schema_registry_healthcheck(cls, _root, _info, **_kwargs):
        schemas = await SchemaDb.query.where(
            SchemaDb.deleted.isnot(None),
        ).gino.all()
        connections_services = await gather(
            [
                ping_service(
                    None,
                    None,
                    None,
                    None,
                    name=schema.service_name,
                    url=schema.url,
                )
                for schema in schemas
            ],
        )
        return Healthcheck(
            branch=BRANCH,
            version=VERSION,
            commit=COMMIT,
            service=settings.ENVVAR_PREFIX_FOR_DYNACONF.lower(),
            connections=[
                Connection(
                    name='postgresql',
                    status=await ping_db(),
                    host=settings.POSTGRES.host,
                    port=settings.POSTGRES.port,
                ),
                *connections_services,
            ],
        )
