import os
import uuid
from argparse import Namespace
from contextlib import contextmanager
from datetime import datetime
from types import SimpleNamespace
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

import graphene
from alembic.config import Config
from faker import Faker
from gino.declarative import ModelType as GinoModel
from sqlalchemy_utils import (
    create_database,
    drop_database,
)
from yarl import URL

from schema_registry import __name__ as project_name
from schema_registry.conf import PROJECT_PATH

fake = Faker()


@contextmanager
def tmp_database(db_url: URL, suffix: str = '', **kwargs) -> str:
    """
    Контекс менеджер для создания тестовой БД и последующего удаления
    """
    # Имя временой БД
    tmp_db_name = '.'.join([uuid.uuid4().hex, project_name, suffix])
    # В URL боевой БД заменяем ее имя на имя временной БД
    tmp_db_url = str(db_url.with_path(tmp_db_name))

    # Создаем тестовую БД
    create_database(tmp_db_url, **kwargs)

    try:
        yield tmp_db_url
    finally:
        drop_database(tmp_db_url)


def make_alembic_config(cmd_opts: Union[Namespace, SimpleNamespace],
                        base_path: str = PROJECT_PATH) -> Config:
    """
    Создаем конфигурационный файл Алембика
    """
    # Replace path to alembic.ini file to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name,
                    cmd_opts=cmd_opts)

    config.set_main_option(
        'script_location',
        os.path.join(base_path, 'db', 'alembic'),
    )

    if cmd_opts.pg_url:
        config.set_main_option('sqlalchemy.url', cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url: Optional[str] = None) -> Config:
    """
    Объект-имитация данных для alembic.ini
    """
    cmd_options = SimpleNamespace(
        config='alembic.ini', name='alembic', pg_url=pg_url,
        raiseerr=False, x=None,
    )
    return make_alembic_config(cmd_options)


def fake_dict(obj, to_ignore: List[str] = None) -> Dict:
    """
    Функция заполнения фейковыми данными полей на основе типов данных
    graphene.types (graphene-gino obj) или sqlalchemy.sql.sqltypes (gino model).
    :param obj: объект содержащий в себе поля классы типов данных
    :param to_ignore: поля, которые следует опустить
    :return: возвращает словарь фейковых данных
    """
    attributes = []
    # Если crud объект из graphene-gino
    # TODO более надежный способ определения graphene-gino crud объекта?
    if hasattr(obj, '__get_fields__'):
        _, schema = obj.__get_fields__(obj._meta)
        attributes = [(key, schema.get(key).type) for key in schema if not key.startswith('_')]
    # Если модель Gino
    elif isinstance(obj, GinoModel):
        gino_model = obj
        attributes = [(column.key, column.type) for column in gino_model]
    # Если graphene.ObjectType
    else:
        schema = obj.__dict__
        attributes = [(key, schema.get(key)) for key in schema if not key.startswith('_')]
    to_ignore = to_ignore or []
    ignore_fields = [
        'id',
        'date_start',
        'date_created',
        'date_deleted',
        'date_updated',
        'is_deleted',
        'starting_point_id',
        *to_ignore
    ]
    test_attributes = {}
    for field_name, field_type in attributes:
        if field_name in ignore_fields:
            continue
        else:
            value = types_converter(field_type)
        if value is not None:
            test_attributes[field_name] = value
            if field_name in ['execution_duration_code', 'reporting_duration_code', 'start_duration_code', 'end_duration_code']:
                test_attributes[field_name] = 'days'
            if field_name in ['number', 'event_type']:
                test_attributes[field_name] = '1'
        else:
            print('UnknownTypeError: {0}'.format(field_type))
    return test_attributes


def types_converter(type_cls, field_name=None):
    """
    Маппинг всех возможных типов данных с рандомными возможными значениями
    :param type_cls: класс-тип данных
    :return:
    """
    if hasattr(type_cls, 'of_type'):
        type_cls = type_cls.of_type
    field_type = str(type_cls).lower()
    if field_type == 'uuid':
        return fake.uuid4()
    if field_type == 'uuid[]':
        return [fake.uuid4()]
    if field_type == 'date':
        return datetime.now().date()
    if field_type == 'datetime':
        return datetime.now()
    if field_type == 'boolean':
        return False
    if field_type in ['int', 'integer']:
        return fake.pyint()
    if field_type == 'float':
        return fake.pyfloat(right_digits=1, min_value=0)
    if field_type == 'decimal':
        return float(fake.pydecimal(positive=True))
    if field_type in ['string', 'varchar']:
        return fake.pystr(8, 16)
    if field_type == 'json':
        return {}
    if field_type == 'jsonstring':
        return '{}'  # noqa: P103


def converter_graphene(attribute):
    """
    Функция конвертирования типов graphene
    :param attribute: аттрибут модели в graphene
    :return:
    """
    if isinstance(attribute, graphene.types.UUID):
        return types_converter('uuid')
    if isinstance(attribute, graphene.types.String):
        return types_converter('string')
    if isinstance(attribute, graphene.types.Date):
        return types_converter('date')
    if isinstance(attribute, graphene.types.DateTime):
        return types_converter('datetime')
    if isinstance(attribute, graphene.types.Boolean):
        return types_converter('boolean')
    if isinstance(attribute, graphene.types.Int):
        return types_converter('int')
    if isinstance(attribute, graphene.types.Float):
        return types_converter('float')
    if isinstance(attribute, graphene.types.Decimal):
        return types_converter('decimal')
    if isinstance(attribute, graphene.types.JSONString):
        return types_converter('jsonstring')


def create_input(test_inputs):
    """
    :param test_inputs: словарь тестовых данных
    :return: строка для запроса graphene
    """
    inputs = ', '.join([convert_input(test_input, test_inputs[test_input]) for test_input in test_inputs])
    return inputs.replace('True', 'true').replace('False', 'false')


def convert_input(key, value):
    """
    :param key: ключ
    :param value: значение
    :return: строка для данных в запросе graphene
    """
    if isinstance(value, (int, float)):
        return '{}: {}'.format(key, value) # noqa: P101
    if isinstance(value, list):
        return '{}: ["{}"]'.format(key, value[0])  # noqa: P101
    return '{}: "{}"'.format(key, value)  # noqa: P101


def convert_type(input_attributes: Dict) -> Dict:
    """
    Конвертер Datetime из строкового представления в Datetime
    :param input_attributes: массив атрибутов для создания объекта
    :return: массив атрибутов для создания объекта
    """
    for key, value in input_attributes.items():
        if isinstance(value, datetime):
            input_attributes[key] = value.isoformat()
        else:
            continue
    return input_attributes
