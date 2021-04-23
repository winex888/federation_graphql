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

from schema_registry.api.models import (
    NotValidSubscriptionSchema,
    SubscriptionSchema,
    update_or_create_schema,
)
from schema_registry.api.types import (
    InputField,
    InputOperation,
)
from schema_registry.api.types import SubscriptionSchema as SubscriptionSchemaGraph
from schema_registry.api.validators import (
    check_exist_not_valid_subscription_schema,
    check_validate_subscription_schema,
)


class CreateOrUpdateSubscriptionSchemaService(ClientIDMutation):

    class Input:
        service_name = String(description=SubscriptionSchema.service_name.doc, required=True)
        port = Int(description=SubscriptionSchema.port.doc, required=True)
        host = String(description=SubscriptionSchema.host.doc, required=True)
        endpoint = String(description=SubscriptionSchema.endpoint.doc, required=True)
        subscription_endpoint = String(description=SubscriptionSchema.subscription_endpoint.doc, required=True)
        graphql_schema = String(description=SubscriptionSchema.graphql_schema.doc, required=True)
        status = Int(description=SubscriptionSchema.status.doc, required=False)
        fields = List(InputField, description='Все поля у схемы', required=True)
        operations = List(InputOperation, description='Все операции у схемы', required=True)

    schema = Field(SubscriptionSchemaGraph, description='Схема')
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
            subscription_endpoint,
            graphql_schema,
            fields,
            operations,
            status=1,
    ):
        schema = SubscriptionSchema
        is_validate, message = await check_validate_subscription_schema(service_name, operations, fields)
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
            schema = NotValidSubscriptionSchema
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
            subscription_endpoint,
        )
        if not is_validate:
            await schema.update(
                validation_errors=message,
            ).apply()
        asyncio.ensure_future(
            check_exist_not_valid_subscription_schema(),
        )
        return CreateOrUpdateSubscriptionSchemaService(
            SubscriptionSchemaGraph(
                id=schema.id,
                service_name=schema.service_name,
                port=schema.port,
                host=schema.host,
                endpoint=endpoint,
                subscription_endpoint=subscription_endpoint,
                status=schema.status,
                graphql_schema=schema.graphql_schema,
                created=schema.created,
                last_update=schema.last_update,
                deleted=schema.deleted,
            ),
            validation_errors=message,
        )


class UpdateSubscriptionSchemaStatus(ClientIDMutation):

    class Input:
        service_name = String(description=SubscriptionSchema.service_name.doc, required=True)
        status = Int(description=SubscriptionSchema.status.doc, required=True)

    schema = Field(SubscriptionSchemaGraph, description='Схема')

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
        schema = await SubscriptionSchema.query.where(SubscriptionSchema.service_name == service_name).gino.first()
        if schema:
            await schema.update(
                status=status,
            ).apply()
        else:
            raise GraphQLError('Схема не найдена')

        return UpdateSubscriptionSchemaStatus(
            SubscriptionSchemaGraph(
                id=schema.id,
                service_name=schema.service_name,
                port=schema.port,
                host=schema.host,
                endpoint=schema.endpoint,
                subscription_endpoint=schema.subscription_endpoint,
                status=schema.status,
                graphql_schema=schema.graphql_schema,
                created=schema.created,
                last_update=schema.last_update,
                deleted=schema.deleted,
            ),
        )


class ValidateServiceSubscriptionSchema(ClientIDMutation):
    class Input:
        service_name = String(description=SubscriptionSchema.service_name.doc, required=True)
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
        is_validate, message = await check_validate_subscription_schema(service_name, operations, fields)
        logging.info(
            'Валидация схемы для {service_name} прошла c результатом {is_validate} {message}'.format(
                service_name=service_name,
                is_validate=is_validate,
                message='ошибки: {message}'.format(
                    message=message,
                ) if message else '',
            ),
        )
        return ValidateServiceSubscriptionSchema(
            validation_errors=message,
        )


class SubscriptionSchemaMutation(ObjectType):

    CreateOrUpdateSubscriptionSchemaService = CreateOrUpdateSubscriptionSchemaService.Field(
        description='Создать или обновить SDL схему для сервиса с подписками',
    )
    UpdateSubscriptionSchemaStatus = UpdateSubscriptionSchemaStatus.Field(
        description='Обновить статус для сервиса с подписками SDL схемы. 0-деактивировать, 1-активировать',
    )
    ValidateServiceSubscriptionSchema = ValidateServiceSubscriptionSchema.Field(
        description='Валидация SDL схемы для сервиса с подписками',
    )
