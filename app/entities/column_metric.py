# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 15:03
# @Author : KarryLiu
# File : column_metric
# @Project : data_agent
from dataclasses import dataclass

@dataclass
class ColumnMetric:
    column_id: str
    metric_id: str

