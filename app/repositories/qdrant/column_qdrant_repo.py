# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 15:50
# @Author : KarryLiu
# File : column_qdrant_repo
# @Project : data_agent
class ColumnQdrantRepo:
    def __init__(self, qdrant_client):
        self.qdrant_client = qdrant_client