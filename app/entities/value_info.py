# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 10:30
# @Author : KarryLiu
# File : value_info
# @Project : data_agent
from dataclasses import dataclass


@dataclass
class ValueInfo:
    id: str
    value: str
    column_id: str
