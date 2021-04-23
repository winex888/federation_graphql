import asyncio
from asyncio.log import logger

import aiohttp_cors
from gql import gql
from aiohttp import web
import graphene
from aiohttp_graphql import GraphQLView

from graphene_federation.entity import custom_entities, key
from graphene_federation.service import get_sdl
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphene_federation import build_schema, extend, external

from gql import Client
from gql.transport.requests import RequestsHTTPTransport

from conf import settings

HOST_TEMPLATE = '{protocol}://{host}:{port}/{endpoint}'


def make_gql_client(protocol, host, port, endpoint) -> Client:
    """
    Создать клиента для взаимодествия с внешними сервисами путем GQL запросов
    """
    transport = RequestsHTTPTransport(
        url=HOST_TEMPLATE.format(
            protocol=protocol,
            host=host,
            port=port,
            endpoint=endpoint,
        ),
        use_json=True,
        headers={
            'Content-type': 'application/json',
        },
        verify=False,
        retries=3,
    )

    client = Client(
        transport=transport,
        fetch_schema_from_transport=False,
    )
    return client


plan_client = make_gql_client(
    protocol='http',
    host=settings.S_HOST,
    port=settings.S_PORT,
    endpoint=settings.S_ENDPOINT,
)

goods = [
    {'id': 1, 'name': 'Пр1', 'price': 1, 'gtype_id': 1},
    {'id': 2, 'name': 'Пр2', 'price': 2, 'gtype_id': 2},
    {'id': 3, 'name': 'Пр3', 'price': 3, 'gtype_id': 3},
    {'id': 4, 'name': 'Пр4', 'price': 4, 'gtype_id': 1},
]

@extend(fields='id')
class GType(graphene.ObjectType):
    id = external(graphene.Int())


@key(fields='id')
class Good(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    price = graphene.Float()
    gtype_id = graphene.Int()
    gtype = graphene.Field(GType)

    def resolve_gtype(self, info, **kwargs):
        return GType(self.gtype_id)

    def __resolve_reference(self, _info, **kwargs):
        logger.error('service2')
        return Good(**goods[self.id-1])


class Query(graphene.ObjectType):

    service2 = graphene.String()
    goods = graphene.List(Good)

    async def resolve_goods(self, _info, **kwargs):
        logger.error('service2')
        return [Good(**item) for item in goods]

    @classmethod
    async def resolve_service2(cls, _root, _info, **_kwargs):
        logger.error('service2')
        return "service2"


schema = build_schema(
    query=Query,
)

gql_view = GraphQLView(
    schema=schema,
    graphiql=False,
    enable_async=True,
    executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
)


def init_routes(app, cors):
    resource = cors.add(app.router.add_resource('/graphql'), {
        '*': aiohttp_cors.ResourceOptions(
            expose_headers='*',
            allow_headers='*',
            allow_credentials=True,
            allow_methods=['POST', 'PUT', 'GET']),
    })
    resource.add_route('POST', gql_view)
    resource.add_route('PUT', gql_view)
    resource.add_route('GET', gql_view)


def init_app(loop=None) -> web.Application:
    if loop is None:
        loop = asyncio.get_event_loop()
    app = web.Application(
        loop=loop,
    )
    cors = aiohttp_cors.setup(app)
    init_routes(app, cors)
    return app


mut = gql('''
mutation r($input: CreateOrUpdateSchemaServiceInput!){
  CreateOrUpdateSchemaService(input: $input){
    schema {
      id      
    }
    
  }
}
''')

if __name__ == '__main__':
    params = {'input': {'host': settings.HOSTN,
                        'endpoint': settings.ENDPOINT,
              'port': settings.NGINX_PORT,
              'serviceName': settings.NAME,
              'graphqlSchema': get_sdl(schema, custom_entities),
                        'fields': [{'name': 'deth345fds', 'extend': False, 'external': False}],
                        'operations': [{'name': 'sqqqwwdf'}]
              }}
    try:
        response = plan_client.execute(mut, variable_values=params)
    except Exception as e:
        pass
    app = init_app()
    web.run_app(app, host=settings.HOST, port=settings.PORT)
