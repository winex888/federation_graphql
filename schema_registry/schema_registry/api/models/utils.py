import logging
from typing import (
    Dict,
    List,
)

from schema_registry.api.models.field import Field
from schema_registry.api.models.gino import db
from schema_registry.api.models.operation import Operation
from schema_registry.conf import settings


async def update_or_create_schema(
        schema_db,
        service_name: str,
        port: int,
        host: str,
        endpoint: str,
        graphql_schema: str,
        fields: List,
        operations: List,
        status: int,
        subscription_endpoint=None,
):
    data_updated = dict(
        service_name=service_name,
        port=port,
        host=host,
        endpoint=endpoint,
        status=status,
        graphql_schema=graphql_schema,
    )
    if subscription_endpoint:
        data_updated['subscription_endpoint'] = subscription_endpoint
    async with db.transaction() as _:
        schema = await schema_db.query.where(
            schema_db.service_name == service_name,
        ).where(
            schema_db.deleted.is_(None),
        ).gino.first()
        if schema:
            logging.info(
                'Обновление схемы {service_name} c типом {schema_type}'.format(
                    service_name=service_name,
                    schema_type=schema_db.__name__,
                ),
            )

            await schema.update(
                **data_updated,
            ).apply()
            await delete_nested_objects(schema.id, Field)
            await delete_nested_objects(schema.id, Operation)
        else:
            logging.info(
                'Создание схемы {service_name} c типом {schema_type}'.format(
                    service_name=service_name,
                    schema_type=schema_db.__name__,
                ),
            )
            schema = await schema_db.create(
                **data_updated,
            )
        updated = {'schema_id': schema.id}
        await create_nested_objects(Field, [update_attribute(field, updated) for field in fields])
        await create_nested_objects(
            Operation,
            [
                update_attribute(operation, updated)
                for operation in operations
                if operation.get('name') not in settings.SERVICE_OPERATIONS
            ],
        )
        return schema


async def delete_nested_objects(schema_id, model):
    return await model.delete.where(model.schema_id == schema_id).gino.status()


async def create_nested_objects(model, objects):
    return await model.bulk_insert(
        objects,
    )


def update_attribute(field: Dict, update: Dict) -> Dict:
    field.update(update)
    return field


def del_keys(obj: Dict, keys: List[str]) -> Dict:
    for key in keys:
        obj.pop(key, None)
    return obj


async def cascade_delete(obj, nested_objects: List, relation_key: str) -> None:
    async with db.transaction() as _:
        for nested_object in nested_objects:
            await nested_object.delete.where(
                getattr(nested_object, relation_key) == obj.id,
            ).gino.status()
        await obj.delete()
