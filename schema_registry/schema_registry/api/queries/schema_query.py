from graphene import (
    List,
    ObjectType,
)

from schema_registry.api.models import Schema as SchemaDb
from schema_registry.api.types import Schema as SchemaGraph


class SchemaQuery(ObjectType):

    all_schemas = List(SchemaGraph)

    @classmethod
    async def resolve_all_schemas(cls, _root, _info, **_kwargs):
        schemas = await SchemaDb.query.where(
            SchemaDb.status == 1,
        ).gino.all()
        return [
            SchemaGraph(
                id=schema.id,  # NOQA: A003
                service_name=schema.service_name,
                port=schema.port,
                host=schema.host,
                endpoint=schema.endpoint,
                status=schema.status,
                graphql_schema=schema.graphql_schema,
                created=schema.created,
                last_update=schema.last_update,
                deleted=schema.deleted,
            ) for schema in schemas
        ]
