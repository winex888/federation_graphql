from graphene import Schema

from schema_registry.api.mutations import (
    SchemaMutation,
    SubscriptionSchemaMutation,
)
from schema_registry.api.queries import (
    HealthcheckQuery,
    SchemaQuery,
    SubscriptionSchemaQuery,
)


class Query(
    HealthcheckQuery,
    SubscriptionSchemaQuery,
    SchemaQuery,
):
    """Все запросы на получение данных."""
    pass


class Mutation(
    SchemaMutation,
    SubscriptionSchemaMutation,
):
    """Все мутации для изменения данных."""
    pass


schema = Schema(
    query=Query,
    mutation=Mutation,
)
