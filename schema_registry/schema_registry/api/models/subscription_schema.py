from schema_registry.api.models.abstract_schema import AbstractSchema
from schema_registry.api.models.gino import db


class SubscriptionSchema(AbstractSchema):
    __tablename__ = 'subscription_schema'

    subscription_endpoint = db.Column(db.String, nullable=False, doc='subscription graphQl endpoin сервиса')

    def __init__(self, **kw):
        super().__init__(**kw)
        self._operations = set()
        self._fields = set()

    @property
    def operations(self):
        return self._operations

    @operations.setter
    def operations(self, operation):
        self._operations.add(operation)

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, field):
        self._fields.add(field)
