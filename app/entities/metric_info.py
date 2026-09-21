# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 15:03
# @Author : KarryLiu
# File : metric_info
# @Project : data_agent
from dataclasses import dataclass

@dataclass
class MetricInfo:
    id: str
    name: str | None
    description: str | None
    relevant_columns: list[str] | None
    alias: list[str] | None

