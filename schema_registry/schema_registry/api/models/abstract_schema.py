import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from schema_registry.api.models.gino import db


class AbstractSchema(db.Model):
    __abstract__ = True

    id = db.Column(UUID, primary_key=True, default=uuid.uuid4,  # noqa A003
                   unique=True, nullable=False,
                   doc='Уникальный идентификатор схемы')
    service_name = db.Column(db.String, nullable=False, doc='Название сервиса')
    port = db.Column(db.Integer, nullable=False, doc='Порт сервиса')
    host = db.Column(db.String, nullable=False, doc='Host сервиса')
    endpoint = db.Column(db.String, nullable=False, doc='graphQl endpoin сервиса')
    status = db.Column(db.Integer, nullable=False, doc='Статус')
    graphql_schema = db.Column(db.String, nullable=False, doc='GraphQL схема')
    created = db.Column(db.DateTime, nullable=False, default=datetime.now, doc='Дата создания')
    last_update = db.Column(db.DateTime, nullable=False, default=datetime.now,
                            onupdate=datetime.now, doc='Дата редактирования')
    deleted = db.Column(db.DateTime, nullable=True, default=None, doc='Дата удаления')
