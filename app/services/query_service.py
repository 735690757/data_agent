# _*_ coding : utf-8 _*_
# @Time : 2026/10/6 16:53
# @Author : KarryLiu
# File : query_service
# @Project : data_agent
import json

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.repositories.es.value_es_repo import ValueESRepo
from app.repositories.mysql.dw.dw_mysql_repo import DWMySQLRepo
from app.repositories.mysql.meta.meta_mysql_repo import MetaMySQLRepo
from app.repositories.qdrant.column_qdrant_repo import ColumnQdrantRepo
from app.repositories.qdrant.metric_qdrant_repo import MetricQdrantRepo


class QueryService:
    def __init__(
            self,
            meta_mysql_repo: MetaMySQLRepo,
            embedding_client: HuggingFaceEndpointEmbeddings,
            dw_mysql_repo: DWMySQLRepo,
            column_qdrant_repo: ColumnQdrantRepo,
            metric_qdrant_repo: MetricQdrantRepo,
            value_es_repo: ValueESRepo
    ):
        self.meta_mysql_repo = meta_mysql_repo
        self.embedding_client = embedding_client
        self.dw_mysql_repo = dw_mysql_repo
        self.column_qdrant_repo = column_qdrant_repo
        self.metric_qdrant_repo = metric_qdrant_repo
        self.value_es_repo = value_es_repo

    async def query(self, query: str):
        try:
            async for chunk in graph.astream(
                    input=DataAgentState(
                        error=None,
                        query=query
                    ),
                    context=DataAgentContext(
                        column_qdrant_repo=self.column_qdrant_repo,
                        metric_qdrant_repo=self.metric_qdrant_repo,
                        value_es_repo=self.value_es_repo,
                        embedding_client=self.embedding_client,
                        meta_mysql_repo=self.meta_mysql_repo,
                        dw_mysql_repo=self.dw_mysql_repo
                    ),
                    stream_mode='custom',
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"
        except Exception as e:
            error = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error, ensure_ascii=False, default=str)}\n\n"
