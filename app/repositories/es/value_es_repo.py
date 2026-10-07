# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 10:14
# @Author : KarryLiu
# File : value_es_repo
# @Project : data_agent
from dataclasses import asdict

from elasticsearch import AsyncElasticsearch

from app.entities.value_info import ValueInfo


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

    async def index(self, value_infos, batch_size=20):
        for i in range(0, len(value_infos), batch_size):
            batch = value_infos[i:i + batch_size]

            batch_operations = []

            for value_info in batch:
                batch_operations.append({
                    "index": {
                        "_index": self.index_name,
                    }
                })
                batch_operations.append(asdict(value_info))

            await self.client.bulk(operations=batch_operations)

    async def search(self, keyword: str, score_threshold: float, limit: int):
        # 这里应该使用 Elasticsearch 的搜索功能，而不是 Qdrant
        result = await self.client.search(
            index=self.index_name,
            query={
                "match": {
                    "value": {
                        "query": keyword,
                    }
                }
            },
            size=limit,
            min_score=score_threshold
        )
        return [ValueInfo(**hit["_source"]) for hit in result["hits"]["hits"]]
