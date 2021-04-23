import asyncio
from asyncio.log import logger

import aiohttp_cors
from gql import gql
from aiohttp import web
import graphene
from aiohttp_graphql import GraphQLView
from graphene_federation import build_schema, extend, external
from graphene_federation.entity import custom_entities
from graphene_federation.service import get_sdl
from graphql.execution.executors.asyncio import AsyncioExecutor

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



@extend(fields='id')
class Good(graphene.ObjectType):
    id = external(graphene.Int())


class Doc(graphene.ObjectType):
    number = graphene.String()
    goods = graphene.Field(Good)
    good_id = graphene.Int()

    def resolve_goods(self, info, **kwargs):
        return Good(self.good_id)


class Query(graphene.ObjectType):

    service1 = graphene.String()
    docs = graphene.List(Doc)

    @classmethod
    async def resolve_docs(cls, _root, _info, **_kwargs):
        logger.error('Service1')
        return [
            Doc(number='3331', good_id=1),
            Doc(number='3332', good_id=2),
            Doc(number='3333', good_id=3),
            Doc(number='3334', good_id=4)
        ]

    @classmethod
    async def resolve_service1(cls, _root, _info, **_kwargs):
        logger.error('Service1')
        return "Service1"


schema = build_schema(
    query=Query,
)

gql_view = GraphQLView(
    schema=schema,
    graphiql=False,
    enable_async=True,
    executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
)


async def info(_request):
    return web.json_response({'data': 'info'})


def init_routes(app, cors):
    app.router.add_get('/info', info)
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
                        'fields': [{'name':'dfds','extend':False, 'external':False}],
                        'operations': [{'name': 'sdf'}]
              }}
    try:
        response = plan_client.execute(mut, variable_values=params)
        logger.error(response)
    except Exception as e:
        logger.error(e)
        pass
    logger.error('fsdfsdfsdfgsdf gsdfgs fg')
    app = init_app()
    web.run_app(app, host=settings.HOST, port=settings.PORT)
