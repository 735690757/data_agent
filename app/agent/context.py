# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:44
# @Author : KarryLiu
# File : context
# @Project : data_agent
from typing import TypedDict

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.repositories.es.value_es_repo import ValueESRepo
from app.repositories.mysql.dw.dw_mysql_repo import DWMySQLRepo
from app.repositories.mysql.meta.meta_mysql_repo import MetaMySQLRepo
from app.repositories.qdrant.column_qdrant_repo import ColumnQdrantRepo
from app.repositories.qdrant.metric_qdrant_repo import MetricQdrantRepo


class DataAgentContext(TypedDict):
    column_qdrant_repo: ColumnQdrantRepo
    embedding_client: HuggingFaceEndpointEmbeddings
    metric_qdrant_repo: MetricQdrantRepo
    value_es_repo: ValueESRepo
    meta_mysql_repo: MetaMySQLRepo
    dw_mysql_repo: DWMySQLRepo
