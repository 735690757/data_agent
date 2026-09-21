# _*_ coding : utf-8 _*_
# @Time : 2026/9/14 16:46
# @Author : KarryLiu
# File : es_client_manager
# @Project : data_agent
from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    def __init__(self, config: ESConfig):
        self.config: ESConfig = config
        self.client: AsyncElasticsearch | None = None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncElasticsearch(
            hosts=[self._get_url()]
        )

    async def close(self):
        if self.client:
            await self.client.close()


es_client_manager = ESClientManager(app_config.es)

if __name__ == '__main__':
    es_client_manager.init()

    client = es_client_manager.client


    async def test():
        # 创建索引
        await client.indices.create(index="test_index", ignore=400)

        await client.index(
            index="books",
            document={
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "date": "1925-04-10",
                "summary": "A novel set in the Jazz Age that tells the story of Jay Gatsby's unrequited love for Daisy Buchanan.",
            }
        )

        resp = await client.search(
            index="books",
        )

        print(resp)

        await client.close()




    import asyncio

    asyncio.run(test())
