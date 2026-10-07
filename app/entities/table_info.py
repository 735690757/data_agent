# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 15:03
# @Author : KarryLiu
# File : table_info
# @Project : data_agent
from dataclasses import dataclass


@dataclass
class TableInfo:
    id: str
    name: str
    role: str
    description: str
