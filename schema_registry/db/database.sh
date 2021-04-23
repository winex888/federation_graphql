#!/bin/bash
CONFIGFILE=/etc/krontech/config # Общий кофигурационный файл с переменными
CONFIGPY='schema_registry.conf' # Путь до файла настроек для include питона откуда брать переменные

set -a
if [ -d "./venv" ]; then
  source ./venv/bin/activate
fi
if [ -e $CONFIGFILE ]; then source $CONFIGFILE || true; fi

# Использовать алембик для создания структуры БД
USE_ALEMBIC=$(python3 -c "from ${CONFIGPY} import USE_ALEMBIC; print(USE_ALEMBIC)")
# Установить расширение postgis
CREATE_POSTGIS=$(python3 -c "from ${CONFIGPY} import CREATE_POSTGIS; print(CREATE_POSTGIS)")
BACKUP_DB=$(python3 -c "from ${CONFIGPY} import BACKUP_DB; print(BACKUP_DB)") # Сделать бэкап БД
DROP_DB=$(python3 -c "from ${CONFIGPY} import DROP_DB; print(DROP_DB)") # Удалить БД

# Присваимваем значения для сервера, имени пользователя, паролю и названию БД из конфига сервиса.
# Из питон конфига проще вытаскивать так. Естественно ваши пути импорта будут отличаться, не должны отличаться только переменные
DB_HOST=$(python3 -c "from ${CONFIGPY} import DB_HOST; print(DB_HOST)")
DB_PORT=$(python3 -c "from ${CONFIGPY} import DB_PORT; print(DB_PORT)")
DB_USER=$(python3 -c "from ${CONFIGPY} import DB_USER; print(DB_USER)")
DB_NAME=$(python3 -c "from ${CONFIGPY} import DB_NAME; print(DB_NAME)")
export PGPASSWORD=$(python3  -c "from ${CONFIGPY} import DB_PASSWORD; print(DB_PASSWORD)")

# проверяем наличие бд
DB=`psql -h ${DB_HOST} -U ${DB_USER} -t -d postgres -c "SELECT datname FROM pg_database WHERE datname='${DB_NAME}'"`

if [[ "$DB" ]]; then
        # закрываем все активные сессии бд
        psql -h "${DB_HOST}" -U ${DB_USER} -c "SELECT pg_terminate_backend(pg_stat_activity.pid)
                                               FROM pg_stat_activity
                                               WHERE pg_stat_activity.datname = '${DB_NAME}'
                                               AND pid <> pg_backend_pid();"


        if $BACKUP_DB; then
                DATE=`date +%s`;
                psql -h "${DB_HOST}" -U ${DB_USER} -c "ALTER DATABASE ${DB_NAME} RENAME TO ${DB_NAME}_$DATE;"
        fi
        if $DROP_DB; then
                psql -h "${DB_HOST}" -U ${DB_USER} -c "DROP DATABASE ${DB_NAME};"
                DB=""
        fi
fi

# если БД нет, то создаем новую
if ! [[ "$DB" ]]; then
        psql -h "${DB_HOST}" -U ${DB_USER} -c "CREATE DATABASE ${DB_NAME};" # Cоздаем БД
        if $CREATE_POSTGIS; then
                # установливаем дополнение PostGIS
                psql -h "${DB_HOST}" -U ${DB_USER} -c "CREATE EXTENSION postgis;" ${DB_NAME}
        fi
fi

if $USE_ALEMBIC; then
       alembic upgrade head
fi
