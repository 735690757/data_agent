# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:44
# @Author : KarryLiu
# File : context
# @Project : data_agent
from typing import TypedDict

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.repositories.qdrant.column_qdrant_repo import ColumnQdrantRepo


class DataAgentContext(TypedDict):
    column_qdrant_repo: ColumnQdrantRepo
    embedding_client: HuggingFaceEndpointEmbeddings
