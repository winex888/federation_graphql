from graphene import (
    UUID,
    Boolean,
    DateTime,
    InputObjectType,
    Int,
    ObjectType,
    String,
)

from schema_registry.api.models import (
    Field,
    Operation,
)
from schema_registry.api.models import Schema as SchemaDb


class InputField(InputObjectType):
    name = String(description=Field.name.doc, required=True)
    extend = Boolean(description=Field.extend.doc, required=True)
    external = Boolean(description=Field.external.doc, required=True)


class InputOperation(InputObjectType):
    name = String(description=Operation.name.doc, required=True)


class Schema(ObjectType):
    id = UUID(description=SchemaDb.id.doc)  # NOQA: A003
    service_name = String(description=SchemaDb.service_name.doc)
    port = Int(description=SchemaDb.port.doc)
    host = String(description=SchemaDb.host.doc)
    endpoint = String(description=SchemaDb.endpoint.doc)
    status = Int(description=SchemaDb.status.doc)
    graphql_schema = String(description=SchemaDb.graphql_schema.doc)
    created = DateTime(description=SchemaDb.created.doc)
    last_update = DateTime(description=SchemaDb.last_update.doc)
    deleted = DateTime(description=SchemaDb.deleted.doc)
