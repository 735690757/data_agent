# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 15:14
# @Author : KarryLiu
# File : metric_info_mapper
# @Project : data_agent
from dataclasses import asdict

from app.entities.metric_info import MetricInfo
from app.models.metric_info import MetricInfoMySQL

class MetricInfoMapper:
    @staticmethod
    def to_entity(model: MetricInfoMySQL) -> MetricInfo:
        return MetricInfo(
            id=model.id,
            name=model.name,
            description=model.description,
            relevant_columns=model.relevant_columns,
            alias=model.alias
        )

    @staticmethod
    def to_model(entity: MetricInfo):
        return MetricInfoMySQL(**asdict(entity))
