from graphene import String

from schema_registry.api.models import SubscriptionSchema as SubscriptionSchemaDb
from schema_registry.api.types.schema_objects import Schema


class SubscriptionSchema(Schema):
    subscription_endpoint = String(description=SubscriptionSchemaDb.subscription_endpoint.doc, required=True)
