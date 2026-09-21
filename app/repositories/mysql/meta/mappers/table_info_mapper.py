# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 15:09
# @Author : KarryLiu
# File : table_info_mapper
# @Project : data_agent
from dataclasses import asdict

from app.entities.table_info import TableInfo
from app.models.table_info import TableInfoMySQL


class tableInfoMapper:
    @staticmethod
    def to_entity(table_info_mysql: TableInfoMySQL) -> TableInfo:
        return TableInfo(
            id=table_info_mysql.id,
            name=table_info_mysql.name,
            description=table_info_mysql.description,
            role=table_info_mysql.role,
        )

    @staticmethod
    def to_model(table_info: TableInfo) -> TableInfoMySQL:
        return TableInfoMySQL(
            # 解构语法，实际上就是将table_info对象的属性转换为字典，然后传递给TableInfoMySQL的构造函数
            **asdict(table_info)
        )
