import pytest

from schema_registry.api.models import (
    Schema,
    db,
)
from tests.utils import (
    convert_type,
    fake_dict,
)


@pytest.mark.parametrize(
    'key_graphene, obj_model, input_attributes',
    [
        ('all_schemas', Schema, fake_dict(Schema, to_ignore=['deleted'])),
    ]
)
@pytest.mark.asyncio
async def test(
    migrated_temp_db,
    graphene_client,
    request,
    key_graphene: str,
    obj_model,
    input_attributes,
):
    """
    Проверка query зарпосов к graphene
    :param graphene_client: клиент graphene
    :param migrated_temp_db: пустая БД с миграциями
    :param key_graphene: название ключа для получения данных в graphene
    :param obj_model: gino model
    """
    async with db.with_bind(migrated_temp_db):
        # создаём объект родитель
        # создаём объект для теста
        input_attributes['status'] = 1
        obj = await obj_model.create(**input_attributes)
        query_output_keys = ' '.join(input_attributes.keys())
        query = """
            query {
              %s {
                %s
              }
            }
            """ % (  # noqa: S001
            key_graphene,
            query_output_keys,
        )

        response = await graphene_client.execute(query)
        assert response.get('errors') is None
        response_dict = response['data'][key_graphene][0]
        assert response_dict.keys() == input_attributes.keys()

        for input_attribute in convert_type(input_attributes):
            assert response_dict[input_attribute] == input_attributes[input_attribute]
