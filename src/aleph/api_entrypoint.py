import logging
from pathlib import Path

import sentry_sdk
from aiohttp import web
from configmanager import Config

import aleph.config
from aleph.db.connection import make_engine, make_session_factory
from aleph.services.cache.node_cache import NodeCache
from aleph.services.ipfs import IpfsService
from aleph.services.ipfs.common import make_ipfs_client
from aleph.services.p2p import init_p2p_client
from aleph.services.storage.fileystem_engine import FileSystemStorageEngine
from aleph.storage import StorageService
from aleph.toolkit.monitoring import setup_sentry
from aleph.web import create_aiohttp_app
from aleph.web.controllers.app_state_getters import (
    APP_STATE_CONFIG,
    APP_STATE_MQ_CONN,
    APP_STATE_NODE_CACHE,
    APP_STATE_P2P_CLIENT,
    APP_STATE_SESSION_FACTORY,
    APP_STATE_STORAGE_SERVICE,
)


async def configure_aiohttp_app(
    config: Config,
) -> web.Application:
    with sentry_sdk.start_transaction(name=f"init-api-server"):
        p2p_client = await init_p2p_client(config, service_name=f"api-server-aiohttp")

        engine = make_engine(
            config,
            echo=config.logging.level.value == logging.DEBUG,
            application_name=f"aleph-api",
        )
        session_factory = make_session_factory(engine)

        node_cache = NodeCache(
            redis_host=config.redis.host.value, redis_port=config.redis.port.value
        )

        ipfs_client = make_ipfs_client(config)
        ipfs_service = IpfsService(ipfs_client=ipfs_client)
        storage_service = StorageService(
            storage_engine=FileSystemStorageEngine(folder=config.storage.folder.value),
            ipfs_service=ipfs_service,
            node_cache=node_cache,
        )

        app = create_aiohttp_app()

        app[APP_STATE_CONFIG] = config
        app[APP_STATE_P2P_CLIENT] = p2p_client
        # Reuse the connection of the P2P client to avoid opening two connections
        app[APP_STATE_MQ_CONN] = p2p_client.mq_client.connection
        app[APP_STATE_NODE_CACHE] = node_cache
        app[APP_STATE_STORAGE_SERVICE] = storage_service
        app[APP_STATE_SESSION_FACTORY] = session_factory

    return app


async def create_app() -> web.Application:
    config = aleph.config.app_config

    # TODO: make the config file path configurable
    config_file = Path.cwd() / "config.yml"
    config.yaml.load(str(config_file))

    logging.basicConfig(level=config.logging.level.value)

    if config.sentry.dsn.value:
        setup_sentry(config)

    return await configure_aiohttp_app(config=config)


if __name__ == "__main__":
    import asyncio
    app = asyncio.run(create_app())
    web.run_app(app, host="localhost", port=8000)
