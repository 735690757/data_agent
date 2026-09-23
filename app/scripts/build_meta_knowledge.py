# _*_ coding : utf-8 _*_
# @Time : 2026/9/19 15:38
# @Author : KarryLiu
# File : build_meta_knowledge
# @Project : data_agent
import argparse
import sys
from pathlib import Path

from app.clients.embedding_client_mamager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.clients.mysql_client_mamager import meta_mysql_client_manager, dw_mysql_client_manager
from app.core.log import logger
from app.repositories.es.value_es_repo import ValueESRepo
from app.repositories.mysql.dw.dw_mysql_repo import DWMySQLRepo
from app.repositories.mysql.meta.meta_mysql_repo import MetaMySQLRepo
from app.repositories.qdrant.column_qdrant_repo import ColumnQdrantRepo
from app.repositories.qdrant.metric_qdrant_repo import MetricQdrantRepo
from app.services.meta_knowledge_service import MetaKnowledgeService


async def build(config_path: Path):
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()


    async with (
        meta_mysql_client_manager.session_factory() as meta_session,
        dw_mysql_client_manager.session_factory() as dw_session
    ):
        meta_mysql_repo = MetaMySQLRepo(meta_session)
        dw_mysql_repo = DWMySQLRepo(dw_session)
        column_qdrant_repo = ColumnQdrantRepo(qdrant_client_manager.client)
        metric_qdrant_repo = MetricQdrantRepo(qdrant_client_manager.client)
        value_es_repo = ValueESRepo(es_client_manager.client)

        meta_knowledge_service = MetaKnowledgeService(
            meta_mysql_repo=meta_mysql_repo,
            dw_mysql_repo=dw_mysql_repo,
            column_qdrant_repo=column_qdrant_repo,
            embedding_client=embedding_client_manager.client,
            metric_qdrant_repo=metric_qdrant_repo,
            value_es_repo=value_es_repo
        )
        await meta_knowledge_service.build(config_path)

    await meta_mysql_client_manager.close()
    await dw_mysql_client_manager.close()
    await qdrant_client_manager.close()
    await es_client_manager.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="build_meta_knowledge",
        description='Build meta knowledge.',
    )
    parser.add_argument('-c', '--config', default="../../conf/meta_conf.yaml", help='Input file')

    args = parser.parse_args()
    print(f"Using config file: {args.config}")

    import asyncio

    asyncio.run(build(args.config))
