"""
Тесты на миграции основаны на данном репозитарии
https://github.com/alvassin/alembic-quickstart/blob/master/README_ru.md
"""
from alembic.command import (
    downgrade,
    upgrade,
)
from alembic.config import Config
from alembic.script import ScriptDirectory


def get_revisions(alembic_config: Config):
    """
    Получаем список миграций проекта, сортированный в порядке возрастания
    """
    # Get Alembic configuration object
    config = alembic_config

    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(config)

    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions('base', 'heads'))
    revisions.reverse()
    return revisions


def test_migrations_stairway(test_db_alembic_config: Config):
    """
    Прогоняем тесты для миграций на изначально пустой БД
    Прицип работы теста на миграции (GIF):
    https://github.com/alvassin/alembic-quickstart/blob/master/assets/stairway.gif
    """
    for revision in get_revisions(test_db_alembic_config):
        upgrade(test_db_alembic_config, revision.revision)

        # We need -1 for downgrading first migration (its down_revision is None)
        downgrade(test_db_alembic_config, revision.down_revision or '-1')
        upgrade(test_db_alembic_config, revision.revision)
