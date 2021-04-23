import asyncio
import logging

from graphene import (
    ClientIDMutation,
    Field,
    Int,
    List,
    ObjectType,
    String,
)
from graphql import GraphQLError

from schema_registry.api.models import NotValidSchema
from schema_registry.api.models import Schema as SchemaDb
from schema_registry.api.models import update_or_create_schema
from schema_registry.api.types import (
    InputField,
    InputOperation,
)
from schema_registry.api.types import Schema as SchemaGraph
from schema_registry.api.validators import (
    check_exist_not_valid_schema,
    check_validate,
)


class CreateOrUpdateSchemaService(ClientIDMutation):
    class Input:
        service_name = String(description=SchemaDb.service_name.doc, required=True)
        port = Int(description=SchemaDb.port.doc, required=True)
        host = String(description=SchemaDb.host.doc, required=True)
        endpoint = String(description=SchemaDb.endpoint.doc, required=True)
        graphql_schema = String(description=SchemaDb.graphql_schema.doc, required=True)
        status = Int(description=SchemaDb.status.doc, required=False)
        fields = List(InputField, description='Все поля у схемы', required=True)
        operations = List(InputOperation, description='Все операции у схемы', required=True)

    schema = Field(SchemaGraph, description='Схема')
    validation_errors = String(description='Сообщение о невалидности схемы')

    @classmethod
    async def mutate_and_get_payload(
            cls,
            _root,
            _info,
            service_name,
            port,
            host,
            endpoint,
            graphql_schema,
            fields,
            operations,
            status=1,
    ):
        schema = SchemaDb
        is_validate, message = await check_validate(service_name, operations, fields)
        logging.info(
            'Валидация схемы для {service_name} прошла c результатом {is_validate} {message}'.format(
                service_name=service_name,
                is_validate=is_validate,
                message='ошибки: {message}'.format(
                    message=message,
                ) if message else '',
            ),
        )
        if not is_validate:
            schema = NotValidSchema
        schema = await update_or_create_schema(
            schema,
            service_name,
            port,
            host,
            endpoint,
            graphql_schema,
            fields,
            operations,
            status,
        )
        if not is_validate:
            await schema.update(
                validation_errors=message,
            ).apply()
        asyncio.ensure_future(
            check_exist_not_valid_schema(),
        )
        return CreateOrUpdateSchemaService(
            SchemaGraph(
                id=schema.id,
                service_name=schema.service_name,
                port=schema.port,
                host=schema.host,
                endpoint=endpoint,
                status=schema.status,
                graphql_schema=schema.graphql_schema,
                created=schema.created,
                last_update=schema.last_update,
                deleted=schema.deleted,
            ),
            validation_errors=message,
        )


class UpdateSchemaStatus(ClientIDMutation):
    class Input:
        service_name = String(description=SchemaDb.service_name.doc, required=True)
        status = Int(description=SchemaDb.status.doc, required=True)

    schema = Field(SchemaGraph, description='Схема')

    @classmethod
    async def mutate_and_get_payload(
            cls,
            _root,
            _info,
            service_name,
            status,
    ):
        if status not in (0, 1):
            raise GraphQLError('Разрешенны значение статуса 0,1')
        schema = await SchemaDb.query.where(SchemaDb.service_name == service_name).gino.first()
        if schema:
            await schema.update(
                status=status,
            ).apply()
        else:
            raise GraphQLError('Схема не найдена')

        return CreateOrUpdateSchemaService(
            SchemaGraph(
                id=schema.id,
                service_name=schema.service_name,
                port=schema.port,
                host=schema.host,
                endpoint=schema.endpoint,
                status=schema.status,
                graphql_schema=schema.graphql_schema,
                created=schema.created,
                last_update=schema.last_update,
                deleted=schema.deleted,
            ),
        )


class ValidateServiceSchema(ClientIDMutation):
    class Input:
        service_name = String(description=SchemaDb.service_name.doc, required=True)
        fields = List(InputField, description='Все поля у схемы', required=True)
        operations = List(InputOperation, description='Все операции у схемы', required=True)

    validation_errors = String(description='Сообщение о невалидности схемы')

    @classmethod
    async def mutate_and_get_payload(
            cls,
            _root,
            _info,
            service_name,
            fields,
            operations,
    ):
        is_validate, message = await check_validate(service_name, operations, fields)
        logging.info(
            'Валидация схемы для {service_name} прошла c результатом {is_validate} {message}'.format(
                service_name=service_name,
                is_validate=is_validate,
                message='ошибки: {message}'.format(
                    message=message,
                ) if message else '',
            ),
        )
        return ValidateServiceSchema(
            validation_errors=message,
        )


class SchemaMutation(ObjectType):
    CreateOrUpdateSchemaService = CreateOrUpdateSchemaService.Field(
        description='Создать или обновить SDL схему',
    )
    UpdateSchemaStatus = UpdateSchemaStatus.Field(
        description='Обновить статус SDL схемы. 0-деактивировать, 1-активировать',
    )
    ValidateServiceSchema = ValidateServiceSchema.Field(
        description='Валидация SDL схемы сервиса',
    )
