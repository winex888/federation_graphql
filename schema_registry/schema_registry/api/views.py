import asyncio

from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from schema_registry.api.schema import schema

gql_view = GraphQLView(
    schema=schema,
    graphiql=False,
    enable_async=True,
    executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
)
