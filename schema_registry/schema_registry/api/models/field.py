import uuid

from sqlalchemy.dialects.postgresql import UUID

from schema_registry.api.models.gino import db


class Field(db.Model):
    __tablename__ = 'fields'

    id = db.Column(  # noqa A003
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        doc='Уникальный идентификатор поля',
    )
    schema_id = db.Column(
        UUID,
        nullable=True,
        doc='Ссылка на схему',
        comment='Ссылка на схему',
    )
    name = db.Column(db.String, nullable=False, doc='Имя поля')
    external = db.Column(db.Boolean, nullable=False, doc='')
    extend = db.Column(db.Boolean, nullable=False, doc='')

    @classmethod
    def bulk_insert(cls, values):
        return cls.insert().gino.all(values)
