import uuid

from sqlalchemy.dialects.postgresql import UUID

from schema_registry.api.models.gino import db


class Operation(db.Model):
    __tablename__ = 'operation'

    id = db.Column(  # noqa A003
        UUID,
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        doc='Уникальный идентификатор операции',
    )
    schema_id = db.Column(
        UUID,
        nullable=True,
        doc='Ссылка на схему',
        comment='Ссылка на схему',
    )
    name = db.Column(
        db.String,
        nullable=False,
        doc='Название',
    )

    @classmethod
    def bulk_insert(cls, values):
        return cls.insert().gino.all(values)
