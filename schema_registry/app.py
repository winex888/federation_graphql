import asyncio
import logging.config

import aiohttp_cors
from aiohttp import web

from schema_registry.conf import (
    BRANCH,
    COMMIT,
    VERSION,
    settings,
)
from schema_registry.extensions import (
    close_db,
    init_db,
)
from schema_registry.routes import init_routes


def init_app(loop=None) -> web.Application:
    logging.config.dictConfig(settings.logging_params)
    if loop is None:
        loop = asyncio.get_event_loop()
    app = web.Application(
        loop=loop,
    )
    cors = aiohttp_cors.setup(app)
    init_routes(app, cors)
    app.on_startup.extend(
        [
            init_db,
        ],
    )
    app.on_cleanup.extend(
        [
            close_db,
        ],
    )
    return app


if __name__ == '__main__':
    app = init_app()
    print('======== Version: {0}\n'
          '======== Branch: {1}\n'
          '======== Commit: {2}'
          .format(VERSION, BRANCH, COMMIT))
    web.run_app(app, host=settings.HOST, port=settings.PORT)
