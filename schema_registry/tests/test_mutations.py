import asyncio
import datetime
from random import randint
from uuid import uuid4

import pytest

from schema_registry.api.models import (
    Field,
    Operation,
    Schema,
    SubscriptionSchema,
    create_nested_objects,
    db,
    update_attribute,
)
from tests.utils import (
    convert_type,
    create_input,
    fake,
    fake_dict,
)


@pytest.mark.parametrize(
    'key_graphene, key_output, input_attributes, fields, operations, updated',
    [
        (
                'CreateOrUpdateSchemaService',
                'schema',
                fake_dict(Schema, to_ignore=['status', 'created', 'last_update', 'deleted']),
                [
                    {
                        'name': fake.pystr(8, 16),
                        'extend': False,
                        'external': True,
                    }
                    for i in range(randint(1, 100))
                ],
                [
                    {
                        'name': fake.pystr(8, 16),
                    }
                    for _ in range(randint(1, 100))
                ],
                False,
        ),
        (
                'CreateOrUpdateSchemaService',
                'schema',
                fake_dict(Schema, to_ignore=['status', 'created', 'last_update', 'deleted']),
                [
                    {
                        'name': fake.pystr(8, 16),
                        'extend': False,
                        'external': False,
                    }
                    for _ in range(randint(1, 100))
                ],
                [
                    {
                        'name': fake.pystr(8, 16),
                    }
                    for _ in range(randint(1, 100))
                ],
                True,
        ),
        (
                'CreateOrUpdateSubscriptionSchemaService',
                'schema',
                fake_dict(SubscriptionSchema, to_ignore=['status', 'created', 'last_update', 'deleted']),
                [
                    {
                        'name': fake.pystr(8, 16),
                        'extend': False,
                        'external': True,
                    }
                    for i in range(randint(1, 100))
                ],
                [
                    {
                        'name': fake.pystr(8, 16),
                    }
                    for _ in range(randint(1, 100))
                ],
                False,
        ),
        (
                'CreateOrUpdateSubscriptionSchemaService',
                'schema',
                fake_dict(SubscriptionSchema, to_ignore=['status', 'created', 'last_update', 'deleted']),
                [
                    {
                        'name': fake.pystr(8, 16),
                        'extend': False,
                        'external': False,
                    }
                    for _ in range(randint(1, 100))
                ],
                [
                    {
                        'name': fake.pystr(8, 16),
                    }
                    for _ in range(randint(1, 100))
                ],
                True,
        )
    ]
)
@pytest.mark.asyncio
async def test_create(
        graphene_client,
        migrated_temp_db,
        key_graphene,
        key_output,
        input_attributes,
        fields,
        operations,
        updated,
):
    """
    Тест на создание объекта
    """
    async with db.with_bind(migrated_temp_db):
        # создаем объект для теста

        if updated:
            schema_id = str(uuid4())
            await SubscriptionSchema.create(
                id=schema_id,
                service_name=input_attributes.get('service_name'),
                port=0000,
                host='updated port',
                endpoint='/subscriptions',
                subscription_endpoint='/graphql/subscriptions',
                status=0,
                graphql_schema='updated schema',
            )
            await Schema.create(
                id=schema_id,
                service_name=input_attributes.get('service_name'),
                port=0000,
                host='updated port',
                endpoint='/graphql',
                status=0,
                graphql_schema='updated schema',
            )
            update = {'schema_id': schema_id}
            await create_nested_objects(Field, [update_attribute(field, update) for field in fields])
            await create_nested_objects(Operation, [update_attribute(operation, update) for operation in operations])


        mutation_input = create_input(convert_type(input_attributes))
        mutation_output_keys = ' '.join(input_attributes.keys())

        # мутация
        mutation = """
        mutation {
        %(key_graphene)s (input: {
            %(mutation_input)s
            operations: [%(operations)s]
            fields: [%(fields)s]
            }){
                %(mutation_input_key)s{
                    %(mutation_output_keys)s
                }
            }
        }
        """ % {  # noqa: S001
            'key_graphene': key_graphene,
            'mutation_input': mutation_input,
            'mutation_input_key': key_output,
            'mutation_output_keys': mutation_output_keys,
            'operations': ', '.join(
                [
                    '{name: "%(name)s"}' % {
                        'name': operation.get('name')
                    }
                    for operation in operations
                ]
            ),
            'fields': ', '.join(
                [
                    '{name: "%(name)s", extend: false, external: false}' % {
                        'name': field.get('name')
                    }
                    for field in fields
                ]
            ),
        }

        response = await graphene_client.execute(mutation)
        assert response.get('errors') is None

        response_dict = response['data'][key_graphene][key_output]
        for input_attribute in input_attributes:
            if isinstance(input_attributes[input_attribute], (datetime.date, datetime.datetime)):
                input_attributes[input_attribute] = str(input_attributes[input_attribute])
            assert response_dict[input_attribute] == input_attributes[input_attribute]


@pytest.mark.parametrize(
    'key_graphene, key_output, updated, count_services',
    [
        (
                'CreateOrUpdateSchemaService',
                'schema',
                False,
                100,
        ),
        (
                'CreateOrUpdateSchemaService',
                'schema',
                True,
                100,
        )
    ]
)
@pytest.mark.asyncio
async def test_create_more_services(
        graphene_client,
        migrated_temp_db,
        key_graphene,
        key_output,
        updated,
        count_services: int,
):
    """
    Тест на создание объекта
    """
    schemas = []
    for _ in range(count_services):
        schemas.append(
            {
                'schema': fake_dict(Schema, to_ignore=['status', 'created', 'last_update', 'deleted']),
                'fields': [
                    {
                        'name': fake.pystr(8, 16),
                        'extend': False,
                        'external': False,
                    }
                    for i in range(randint(1, 100))
                ],
                'operations': [
                    {
                        'name': fake.pystr(8, 16),
                    }
                    for _ in range(randint(1, 100))
                ]
            }
        )
    async with db.with_bind(migrated_temp_db):
        # создаем объект для теста
        if updated:
            for schema in schemas:
                schema['schema']['status'] = 0
                sc = await Schema.create(**schema.get('schema'))
                update = {'schema_id': sc.id}
                await create_nested_objects(
                    Field,
                    [update_attribute(field, update) for field in schema.get('fields')]
                )
                await create_nested_objects(
                    Operation,
                    [update_attribute(operation, update) for operation in schema.get('operations')]
                )
        await asyncio.gather(
            *[
                create_schema(
                    graphene_client,
                    key_graphene,
                    key_output,
                    schema.get('schema'),
                    schema.get('operations'),
                    schema.get('fields'),
                )
                for schema in schemas
            ]
        )


async def create_schema(graphene_client, key_graphene, key_output, input_attributes, operations, fields):
    mutation_input = create_input(convert_type(input_attributes))
    mutation_output_keys = ' '.join(input_attributes.keys())

    # мутация
    mutation = """
            mutation {
            %(key_graphene)s (input: {
                %(mutation_input)s
                operations: [%(operations)s]
                fields: [%(fields)s]
                }){
                    %(mutation_input_key)s{
                        %(mutation_output_keys)s
                    }
                    validation_errors
                }
            }
            """ % {  # noqa: S001
        'key_graphene': key_graphene,
        'mutation_input': mutation_input,
        'mutation_input_key': key_output,
        'mutation_output_keys': mutation_output_keys,
        'operations': ', '.join(
            [
                '{name: "%(name)s"}' % {
                    'name': operation.get('name')
                }
                for operation in operations
            ]
        ),
        'fields': ', '.join(
            [
                '{name: "%(name)s", extend: %(extend)s, external: %(external)s}' % {
                    'name': field.get('name'),
                    'external': 'true' if field.get('external') else 'false',
                    'extend': 'true' if field.get('extend') else 'false'
                }
                for field in fields
            ]
        ),
    }

    response = await graphene_client.execute(mutation)
    assert response.get('errors') is None
    assert response.get('validation_errors') is None

    response_dict = response['data'][key_graphene][key_output]
    for input_attribute in input_attributes:
        if isinstance(input_attributes[input_attribute], (datetime.date, datetime.datetime)):
            input_attributes[input_attribute] = str(input_attributes[input_attribute])
        assert response_dict[input_attribute] == input_attributes[input_attribute]
