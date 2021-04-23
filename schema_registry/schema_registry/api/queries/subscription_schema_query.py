from graphene import (
    List,
    ObjectType,
)

from schema_registry.api.models import SubscriptionSchema as SubscriptionSchemaDb
from schema_registry.api.types import SubscriptionSchema as SubscriptionSchemaGraph


class SubscriptionSchemaQuery(ObjectType):

    all_subscription_schemas = List(SubscriptionSchemaGraph)

    @classmethod
    async def resolve_all_subscription_schemas(cls, _root, _info, **_kwargs):
        schemas = await SubscriptionSchemaDb.query.where(
            SubscriptionSchemaDb.status == 1,
        ).gino.all()
        return [
            SubscriptionSchemaGraph(
                id=schema.id,  # NOQA: A003
                service_name=schema.service_name,
                port=schema.port,
                host=schema.host,
                endpoint=schema.endpoint,
                subscription_endpoint=schema.subscription_endpoint,
                status=schema.status,
                graphql_schema=schema.graphql_schema,
                created=schema.created,
                last_update=schema.last_update,
                deleted=schema.deleted,
            ) for schema in schemas
        ]
