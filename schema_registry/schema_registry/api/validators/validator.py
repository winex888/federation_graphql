import json
import logging
from datetime import (
    MINYEAR,
    datetime,
)
from typing import List

from sqlalchemy import and_

from schema_registry.api.models import (
    Field,
    NotValidSchema,
    Operation,
    Schema,
    db,
)
from schema_registry.api.models.utils import (
    cascade_delete,
    del_keys,
    update_or_create_schema,
)


def check_exists_field(external_fields: List[str], extend_fields: List[str]):
    not_exists_external_field = []
    for external_field in external_fields:
        if external_field not in extend_fields:
            not_exists_external_field.append(external_field)
    return not_exists_external_field


async def check_exist_extend_fields(service_name, extend_fields):
    schema = await db.select(
        [Schema, Field],
    ).select_from(
        Schema.outerjoin(
            Field,
            and_(
                Field.schema_id == Schema.id,
                Field.extend.is_(True),
            ),
        ),
    ).where(
        Schema.deleted.is_(None),
    ).where(
        Schema.service_name == service_name,
    ).gino.load(
        Schema.distinct(Schema.id).load(
            fields=Field.distinct(Field.id),
        ),
    ).first()
    if not schema:
        return []
    del_fields = check_exists_field([field.name for field in schema.fields], extend_fields)
    dependent_field = None
    if del_fields:
        dependent_field = await db.select(
            [Field, Schema],
        ).select_from(
            Field.outerjoin(
                Schema,
                and_(
                    Field.schema_id == Schema.id,
                    Field.external.is_(True),
                    Field.name.in_(del_fields),
                ),
            ),
        ).where(
            Schema.deleted.is_(None),
        ).gino.load(
            Field.distinct(Field.id),
        ).all()
    return del_fields if dependent_field else []


async def check_validate(service_name: str, operations: List, fields: List):
    message = ''
    is_validate = True
    external_fields = [
        getattr(field, 'name', None)
        for field in fields
        if getattr(field, 'external', None)
    ]
    extend_fields = [
        getattr(field, 'name', None)
        for field in fields
        if getattr(field, 'extend', None)
    ]
    schemas = await db.select(
        [Schema, Operation, Field],
    ).select_from(
        Schema.outerjoin(
            Operation,
            and_(
                Operation.schema_id == Schema.id,
                Operation.name.in_(
                    [
                        getattr(operation, 'name', None)
                        for operation in operations
                    ],
                ),
            ),
        ).outerjoin(
            Field,
            and_(
                Field.schema_id == Schema.id,
                Field.name.in_(external_fields),
                Field.extend.is_(True),
            ),
        ),
    ).where(
        Schema.deleted.is_(None),
    ).where(
        Schema.service_name != service_name,
    ).gino.load(
        Schema.distinct(Schema.id).load(
            operations=Operation.distinct(Operation.id),
            fields=Field.distinct(Field.id),
        ),
    ).all()

    db_operations = [
        operation.name
        for schema in schemas
        for operation in schema.operations
    ]
    if db_operations:
        is_validate = False
        message += 'Операции(query/mutation) {operations} с таким именем уже есть. \n'.format(
            operations=json.dumps(db_operations),
        )
    if extend_fields:
        forbidden_del_fields = await check_exist_extend_fields(service_name, extend_fields)
        if forbidden_del_fields:
            is_validate = False
            message += 'Extend поля: {forbidden_del_fields},' \
                       ' нельзя удалить. Они используется в' \
                       ' других схемах. \n'.format(
                                            forbidden_del_fields=forbidden_del_fields,
                        )
    if external_fields:
        extend_fields = [
            field
            for schema in schemas
            for field in schema.fields
        ]
        not_exists_external_field = check_exists_field(
            external_fields,
            [extend_field.name for extend_field in extend_fields],
        )
        if not_exists_external_field:
            is_validate = False
            message += '{not_exists_external_field}: этих объектов не обнаружено в extend полях других схем \n'.format(
                not_exists_external_field=json.dumps(not_exists_external_field),
            )
    return is_validate, message or None


async def check_exist_not_valid_schema():
    schemas = await db.select(
        (NotValidSchema, Operation, Field, Schema),
    ).select_from(
        NotValidSchema.outerjoin(
            Operation,
            Operation.schema_id == NotValidSchema.id,
        ).outerjoin(
            Field,
            and_(
                Field.schema_id == NotValidSchema.id,
                Field.external.is_(True),
            ),
        ).outerjoin(
            Schema,
            and_(
                Schema.service_name == NotValidSchema.service_name,
                Schema.deleted.is_(None),
            ),
        ),
    ).where(
        NotValidSchema.deleted.is_(None),
    ).gino.load(
        NotValidSchema.distinct(NotValidSchema.id).load(
            operations=Operation.distinct(Operation.id),
            fields=Field.distinct(Field.id),
            valid_schema=Schema.distinct(Schema.id),
        ),
    ).all()
    for schema in schemas:
        logging.info(
            'Схема {service_name} проверяется на валидность'.format(
                service_name=schema.service_name,
            ),
        )
        if schema.last_update < getattr(schema.valid_schema, 'last_update', datetime(MINYEAR, 1, 1)):
            await cascade_delete(
                schema, [Field, Operation], 'schema_id',
            )
            continue
        is_validate, _ = await check_validate(
            schema.service_name,
            schema.operations,
            schema.fields,
        )
        if is_validate:
            logging.info(
                'Схема {service_name}, после валидации, стала из невалидной валидной'.format(
                    service_name=schema.service_name,
                ),
            )
            async with db.transaction() as _:
                await update_or_create_schema(
                    Schema,
                    schema.service_name,
                    schema.port,
                    schema.host,
                    schema.endpoint,
                    schema.graphql_schema,
                    [del_keys(field.to_dict(), ['id', 'schema_id']) for field in schema.fields],
                    [del_keys(operation.to_dict(), ['id', 'schema_id']) for operation in schema.operations],
                    schema.status,
                )
                await cascade_delete(
                    schema, [Field, Operation], 'schema_id',
                )
