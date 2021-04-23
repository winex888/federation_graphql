import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import (
    engine_from_config,
    pool,
)

# fix путей к пакету
MODEL_PATH = str(Path.cwd())
sys.path.append(MODEL_PATH)

from schema_registry.conf import DSN_STR  # noqa: I001 isort:skip
from schema_registry.api.models import db as target_metadata  # noqa: I001 isort:skip

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Проверяем передан ли нам URL бд для миграций
try:
    pg_url = config.cmd_opts.pg_url
except AttributeError:
    pg_url = None
# Задаем дефолтный URL БД, если явно не передан
if not pg_url:
    config.set_main_option('sqlalchemy.url', str(DSN_STR))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Таблицы, которые не нужно учитывать при генерации миграций
exclude_tables = config.get_section('alembic:exclude').get('tables', '').split(',')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_object(object, name, type_, reflected, compare_to):
    """
    Тут происходит логика выбора какие таблицы учитывать при миграциях
    """
    if type_ == "table" and name in exclude_tables:
        # Исключаем таблицы из "exclude_tables"
        return False
    else:
        return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    def process_revision_directives(context, revision, directives):
        if config.cmd_opts.autogenerate:
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
