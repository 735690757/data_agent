# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:16
# @Author : KarryLiu
# File : state
# @Project : data_agent
from typing import TypedDict

from app.entities.column_info import ColumnInfo


class DataAgentState(TypedDict):
    query: str  # 用户输入的查询语句
    keywords: list[str]  # 用户输入的查询语句中的关键字，经过jieba分词后得到的关键字列表
    retrieve_column_infos: list[ColumnInfo]  # 检索到的列信息列表，每个元素是一个字典，包含列名、表名、数据库名等信息

    error: str  # 校验sql时的错误信息
