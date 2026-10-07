# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 14:39
# @Author : KarryLiu
# File : metric_qdrant_repo
# @Project : data_agent
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

from app.conf.app_config import app_config
from app.entities.metric_info import MetricInfo


class MetricQdrantRepo:
    collection_name = "metric_collection"

    def __init__(self, qdrant_client: AsyncQdrantClient):
        self.qdrant_client = qdrant_client

    async def ensure_collection(self):
        if not await self.qdrant_client.collection_exists(self.collection_name):
            await self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=app_config.qdrant.embedding_size,
                    distance=Distance.COSINE
                )
            )

    async def upsert(self, ids: list[str], embeddings: list[list[float]], payloads: list[dict], batch_size: int = 10):
        """
            await client.upsert(
            collection_name="test_collection_async",
            wait=True,
            points=[
                PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
            ],
        )
        """
        points: list[PointStruct] = [
            PointStruct(id=id, vector=embedding, payload=payload)
            for (id, embedding, payload) in zip(ids, embeddings, payloads)
        ]

        for i in range(0, len(points), batch_size):
            batch_points = points[i:i + batch_size]

            await self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch_points
            )

    async def search(self, embedding_vector:list[float], score_threshold: float, limit:int)-> list[MetricInfo]:
        result = await self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=embedding_vector,
            score_threshold=score_threshold,
            limit=limit
        )
        return [MetricInfo(**point.payload) for point in result.points]

