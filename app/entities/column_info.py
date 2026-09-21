# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 15:03
# @Author : KarryLiu
# File : column_info
# @Project : data_agent
from dataclasses import dataclass
from typing import Any

@dataclass
class ColumnInfo:
    id: str
    name: str
    type: str
    role: str
    examples: list[Any]
    description: str
    alias: list[str]
    table_id: str

