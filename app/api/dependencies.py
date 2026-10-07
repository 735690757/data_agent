# _*_ coding : utf-8 _*_
# @Time : 2026/10/7 13:05
# @Author : KarryLiu
# File : dependencies
# @Project : data_agent
from typing import Annotated

from fastapi import Depends
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.embedding_client_mamager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_mamager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repo import ValueESRepo
from app.repositories.mysql.dw.dw_mysql_repo import DWMySQLRepo
from app.repositories.mysql.meta.meta_mysql_repo import MetaMySQLRepo
from app.repositories.qdrant.column_qdrant_repo import ColumnQdrantRepo
from app.repositories.qdrant.metric_qdrant_repo import MetricQdrantRepo
from app.services.query_service import QueryService


async def get_meta_mysql_session():
    async with meta_mysql_client_manager.session_factory() as session:
        yield session

async def get_dw_mysql_session():
    async with dw_mysql_client_manager.session_factory() as session:
        yield session

async def get_meta_mysql_repo(meta_session: Annotated[AsyncSession, Depends(get_meta_mysql_session)]) -> MetaMySQLRepo:
    return MetaMySQLRepo(meta_session)


async def get_embedding_client() -> HuggingFaceEndpointEmbeddings:
    return embedding_client_manager.client



async def get_dw_mysql_repo(dw_session: Annotated[AsyncSession, Depends(get_dw_mysql_session)]) -> DWMySQLRepo:
    return DWMySQLRepo(dw_session)


async def get_column_qdrant_repo() -> ColumnQdrantRepo:
    return ColumnQdrantRepo(qdrant_client_manager.client)


async def get_metric_qdrant_repo() -> MetricQdrantRepo:
    return MetricQdrantRepo(qdrant_client_manager.client)


async def get_value_es_repo() -> ValueESRepo:
    return ValueESRepo(es_client_manager.client)


async def get_query_service(
        meta_mysql_repo: Annotated[MetaMySQLRepo, Depends(get_meta_mysql_repo)],
        embedding_client: Annotated[HuggingFaceEndpointEmbeddings, Depends(get_embedding_client)],
        dw_mysql_repo: Annotated[DWMySQLRepo, Depends(get_dw_mysql_repo)],
        column_qdrant_repo: Annotated[ColumnQdrantRepo, Depends(get_column_qdrant_repo)],
        metric_qdrant_repo: Annotated[MetricQdrantRepo, Depends(get_metric_qdrant_repo)],
        value_es_repo: Annotated[ValueESRepo, Depends(get_value_es_repo)]
) -> QueryService:


    return QueryService(
        meta_mysql_repo=meta_mysql_repo,
        embedding_client=embedding_client,
        dw_mysql_repo=dw_mysql_repo,
        column_qdrant_repo=column_qdrant_repo,
        metric_qdrant_repo=metric_qdrant_repo,
        value_es_repo=value_es_repo
    )
