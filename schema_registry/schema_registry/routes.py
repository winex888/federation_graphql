import aiohttp_cors
from aiohttp import web

from schema_registry.api.models import (
    Schema,
    SubscriptionSchema,
)
from schema_registry.api.views import gql_view


async def get_schema(_request):
    schema = await Schema.query.where(Schema.status == 1).gino.all()
    data = {
        'data': [
            {
                'service_name': item.service_name,
                'port': item.port,
                'graphql_schema': item.graphql_schema,
                'host': item.host,
                'endpoint': item.endpoint,
            } for item in schema
        ],
    }
    return web.json_response(data)


async def get_subscription_schema(_request):
    schema = await SubscriptionSchema.query.where(SubscriptionSchema.status == 1).gino.all()
    data = {
        'data': [
            {
                'service_name': item.service_name,
                'port': item.port,
                'graphql_schema': item.graphql_schema,
                'host': item.host,
                'endpoint': item.endpoint,
                'subscription_endpoint': item.subscription_endpoint,
            } for item in schema
        ],
    }
    return web.json_response(data)


def init_routes(app, cors):
    app.router.add_get('/schema', get_schema)
    app.router.add_get('/subscription_schema', get_subscription_schema)
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
