from schema_registry.api.models.abstract_schema import AbstractSchema
from schema_registry.api.models.gino import db


class NotValidSchema(AbstractSchema):
    __tablename__ = 'not_valid_schema'

    validation_errors = db.Column(db.String, nullable=True, doc='Ошибки валидации')

    def __init__(self, **kw):
        super().__init__(**kw)
        self._operations = set()
        self._fields = set()
        self._valid_schema = None

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

    @property
    def valid_schema(self):
        return self._valid_schema

    @valid_schema.setter
    def valid_schema(self, valid_schema):
        self._valid_schema = valid_schema
