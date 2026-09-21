# _*_ coding : utf-8 _*_
# @Time : 2026/9/19 16:24
# @Author : KarryLiu
# File : meta_knowledge_service
# @Project : data_agent
from pathlib import Path

from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.repositories.mysql.dw.dw_mysql_repo import DWMySQLRepo
from app.repositories.mysql.meta.meta_mysql_repo import MetaMySQLRepo


class MetaKnowledgeService:
    def __init__(self, meta_mysql_repo: MetaMySQLRepo, dw_mysql_repo: DWMySQLRepo):
        self.meta_mysql_repo: MetaMySQLRepo = meta_mysql_repo  # MetaMySQLRepo
        self.dw_mysql_repo: DWMySQLRepo = dw_mysql_repo  # DWMySQLRepo

    async def build(self, config_path: Path):
        config_file = config_path
        context = OmegaConf.load(config_file)
        schema = OmegaConf.structured(MetaConfig)

        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

        # 存在表信息
        if meta_config.tables:
            table_infos: list[TableInfo] = []
            column_infos: list[ColumnInfo] = []
            # 1. 将表信息和字段信息存储到数据库中（table_info，column_info）
            for table in meta_config.tables:
                # table -> table_info
                table_info = TableInfo(
                    id=table.name,
                    name=table.name,
                    description=table.description,
                    role=table.role,
                )
                table_infos.append(table_info)
                # 查询字段类型

                column_types = await self.dw_mysql_repo.get_column_types(table.name)

                for column in table.columns:
                    # 查询字段取值示例
                    column_values = await self.dw_mysql_repo.get_column_examples(table.name, column.name)
                    # table.columns -> column_info
                    column_info = ColumnInfo(
                        id=f"{table.name}.{column.name}",
                        name=column.name,
                        description=column.description,
                        alias=column.alias,
                        type=column_types.get(column.name),
                        role=column.role,
                        examples=column_values,
                        table_id=table.name
                    )

                    column_infos.append(column_info)
            # print(f"table_infos:")
            # for table_info in table_infos:
            #     print(table_info)
            #
            # print("=" * 50)
            # print(f"column_infos:")
            # for column_info in column_infos:
            #     print(column_info)

            # sync with self.meta_mysql_repo.session.begin():自动管理事务
            async with self.meta_mysql_repo.session.begin():
                self.meta_mysql_repo.save_table_infos(table_infos)
                self.meta_mysql_repo.save_column_infos(column_infos)

            # 2. 对字段信息（column_info），进行向量化，并存储到向量数据库中（qdrant）

            # 3. 对指定的维度字段，建立全文索引
            pass

        # 存在指标信息
        if meta_config.metrics:
            # 1. 将指标信息存储到数据库中（metric_info, column_metric）

            # 2. 对指标信息进行向量化，并存储到向量数据库中（qdrant）
            pass
