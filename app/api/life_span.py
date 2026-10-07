# _*_ coding : utf-8 _*_
# @Time : 2026/10/7 13:21
# @Author : KarryLiu
# File : life_span
# @Project : data_agent
from contextlib import asynccontextmanager

from app.clients.embedding_client_mamager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_mamager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.core.log import logger


@asynccontextmanager
async def lifespan(app):
    # 在应用启动时执行的代码
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()
    logger.info("应用启动完成，所有客户端已初始化")
    yield
    # 在应用关闭时执行的代码
    await qdrant_client_manager.close()
    await es_client_manager.close()
    await meta_mysql_client_manager.close()
    await dw_mysql_client_manager.close()
    logger.info("应用关闭完成，所有客户端已关闭")
