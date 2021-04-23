from schema_registry.api.models.abstract_schema import AbstractSchema


class Schema(AbstractSchema):
    __tablename__ = 'schema'

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
