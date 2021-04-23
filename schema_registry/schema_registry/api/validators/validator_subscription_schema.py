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
    NotValidSubscriptionSchema,
    Operation,
    SubscriptionSchema,
    cascade_delete,
    db,
    del_keys,
    update_or_create_schema,
)


async def check_validate_subscription_schema(service_name: str, operations: List, _fields):
    message = ''
    is_validate = True
    schemas = await db.select(
        [SubscriptionSchema, Operation],
    ).select_from(
        SubscriptionSchema.outerjoin(
            Operation,
            and_(
                Operation.schema_id == SubscriptionSchema.id,
                Operation.name.in_(
                    [
                        getattr(operation, 'name', None)
                        for operation in operations
                    ],
                ),
            ),
        ),
    ).where(
        SubscriptionSchema.deleted.is_(None),
    ).where(
        SubscriptionSchema.service_name != service_name,
    ).gino.load(
        SubscriptionSchema.distinct(SubscriptionSchema.id).load(
            operations=Operation.distinct(Operation.id),
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
    return is_validate, message or None


async def check_exist_not_valid_subscription_schema():
    schemas = await db.select(
        (NotValidSubscriptionSchema, Operation, Field, SubscriptionSchema),
    ).select_from(
        NotValidSubscriptionSchema.outerjoin(
            Operation,
            Operation.schema_id == NotValidSubscriptionSchema.id,
        ).outerjoin(
            Field,
            Field.schema_id == NotValidSubscriptionSchema.id,
        ).outerjoin(
            SubscriptionSchema,
            and_(
                SubscriptionSchema.service_name == NotValidSubscriptionSchema.service_name,
                SubscriptionSchema.deleted.is_(None),
            ),
        ),
    ).where(
        NotValidSubscriptionSchema.deleted.is_(None),
    ).gino.load(
        NotValidSubscriptionSchema.distinct(NotValidSubscriptionSchema.id).load(
            operations=Operation.distinct(Operation.id),
            field=Field.distinct(Field.id),
            valid_schema=SubscriptionSchema.distinct(SubscriptionSchema.id),
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
        is_validate, _ = await check_validate_subscription_schema(
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
                    SubscriptionSchema,
                    schema.service_name,
                    schema.port,
                    schema.host,
                    schema.endpoint,
                    schema.graphql_schema,
                    [del_keys(field.to_dict(), ['id', 'schema_id']) for field in schema.fields],
                    [del_keys(operation.to_dict(), ['id', 'schema_id']) for operation in schema.operations],
                    schema.status,
                    schema.subscription_endpoint,
                )
                await cascade_delete(
                    schema, [Field, Operation], 'schema_id',
                )
