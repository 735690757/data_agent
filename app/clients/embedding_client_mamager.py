# _*_ coding : utf-8 _*_
# @Time : 2026/9/14 20:08
# @Author : KarryLiu
# File : embedding_client_mamager
# @Project : data_agent
from langchain_openai import OpenAIEmbeddings

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.client: OpenAIEmbeddings | None = None
        self.config = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}/v1"

    def init(self):
        self.client = OpenAIEmbeddings(
            model="tei",
            base_url=self._get_url(),
            api_key="dummy",
            check_embedding_ctx_length=False,
        )

embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    embedding_client_manager.init()

    client = embedding_client_manager.client

    text = "Hello, world!"
    embedding = client.embed_query(text)

    print("维度:", len(embedding))
    print("前10维:", embedding[:10])