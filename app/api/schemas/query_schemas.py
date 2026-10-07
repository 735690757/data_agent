# _*_ coding : utf-8 _*_
# @Time : 2026/10/6 13:53
# @Author : KarryLiu
# File : query_schemas
# @Project : data_agent
from pydantic import BaseModel


class QuerySchema(BaseModel):
    query: str
