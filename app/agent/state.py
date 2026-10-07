# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:16
# @Author : KarryLiu
# File : state
# @Project : data_agent
from typing import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo


class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list
    description: str
    alias: list[str]


class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]


class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


class DateInfoState(TypedDict):
    date: str
    weekday: str
    quarter: str


class DBInfoState(TypedDict):
    dialect: str
    version: str


class DataAgentState(TypedDict):
    query: str  # 用户输入的查询语句
    keywords: list[str]  # 用户输入的查询语句中的关键字，经过jieba分词后得到的关键字列表
    retrieve_column_infos: list[ColumnInfo]  # 检索到的列信息列表，每个元素是一个字典，包含列名、表名、数据库名等信息
    retrieve_metric_infos: list[MetricInfo]  # 检索到的指标信息列表，每个元素是一个字典，包含指标名、表名、数据库名等信息
    retrieve_value_infos: list[ValueInfo]  # 检索到的值信息列表，每个元素是一个字典，包含值名、表名、数据库名等信息

    table_infos: list[TableInfoState]  # 检索到的表信息列表，每个元素是一个字典，包含表名、描述等信息
    metric_infos: list[MetricInfoState]  # 检索到的指标信息列表，每个元素是一个字典，包含指标名、表名、数据库名等信息

    date_info: DateInfoState
    db_info: DBInfoState

    sql: str  # 生成的sql语句

    error: str  # 校验sql时的错误信息
