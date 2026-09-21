# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 10:47
# @Author : KarryLiu
# File : meta_config
# @Project : data_agent
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class ColumnConfig:
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool

@dataclass
class TableConfig:
    name: str
    role: str
    description: str
    columns: list[ColumnConfig]

@dataclass
class MetricConfig:
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

@dataclass
class MetaConfig:
    tables: Optional[list[TableConfig]] = None
    metrics: Optional[list[MetricConfig]] = None

