# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 13:43
# @Author : KarryLiu
# File : meta_mysql_repo
# @Project : data_agent
from typing import cast

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.repositories.mysql.meta.mappers.column_info_mapper import ColumnInfoMapper
from app.repositories.mysql.meta.mappers.column_metric_mapper import ColumnMetricMapper
from app.repositories.mysql.meta.mappers.metric_info_mapper import MetricInfoMapper
from app.repositories.mysql.meta.mappers.table_info_mapper import tableInfoMapper


class MetaMySQLRepo:
    def __init__(self, session: AsyncSession):
        self.session = session  # MySQL session

    def read(self):
        pass

    def write(self):
        pass

    def save_table_infos(self, table_infos: list[TableInfo]):
        self.session.add_all([tableInfoMapper.to_model(table_info) for table_info in table_infos])

    def save_column_infos(self, column_infos: list[ColumnInfo]):
        self.session.add_all([ColumnInfoMapper.to_model(column_info) for column_info in column_infos])

    async def save_metric_infos(self, metric_infos: list[MetricInfo]):
        self.session.add_all([MetricInfoMapper.to_model(metric_info) for metric_info in metric_infos])

    async def save_column_metrics(self, column_metrics: list[ColumnMetric]):
        self.session.add_all([ColumnMetricMapper.to_model(column_metric) for column_metric in column_metrics])

    async def get_column_info_by_id(self, id: str) -> ColumnInfo:
        column_info = cast(
            ColumnInfoMySQL | None,
            await self.session.get(ColumnInfoMySQL, id),
        )
        if column_info is None:
            raise ValueError("Column info not found")
        return ColumnInfoMapper.to_entity(column_info)

    async def get_table_info_by_id(self, table_id) -> TableInfo:
        table_info = cast(
            TableInfoMySQL | None,
            await self.session.get(TableInfoMySQL, table_id),
        )
        if table_info is None:
            raise ValueError("Table info not found")
        return tableInfoMapper.to_entity(table_info)

    async def get_key_columns_by_tabele_id(self, table_id) -> list[ColumnInfo]:
        sql = "select * from column_info where table_id = :table_id and role in ('primary_key', 'foreign_key')"
        result = await self.session.execute(text(sql), {"table_id": table_id})
        return [ColumnInfo(**dict(row)) for row in result.mappings().fetchall()]
