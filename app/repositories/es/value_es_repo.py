# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 10:14
# @Author : KarryLiu
# File : value_es_repo
# @Project : data_agent
from elasticsearch import AsyncElasticsearch


class ValueESRepo:
    index_name = "value_index"

    index_mappings = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
            "column_id": {"type": "keyword"}
        }
    }

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def ensure_index(self):
        if not await self.client.indices.exists(index=self.index_name):
            await self.client.indices.create(
                index=self.index_name,
                mappings=self.index_mappings
            )
