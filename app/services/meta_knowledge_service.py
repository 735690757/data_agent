# _*_ coding : utf-8 _*_
# @Time : 2026/9/19 16:24
# @Author : KarryLiu
# File : meta_knowledge_service
# @Project : data_agent
import uuid
from dataclasses import asdict
from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.repositories.es.value_es_repo import ValueESRepo
from app.repositories.mysql.dw.dw_mysql_repo import DWMySQLRepo
from app.repositories.mysql.meta.meta_mysql_repo import MetaMySQLRepo
from app.repositories.qdrant.column_qdrant_repo import ColumnQdrantRepo
from app.repositories.qdrant.metric_qdrant_repo import MetricQdrantRepo
from app.core.log import logger


class MetaKnowledgeService:
    def __init__(self, meta_mysql_repo: MetaMySQLRepo,
                 dw_mysql_repo: DWMySQLRepo,
                 embedding_client: HuggingFaceEndpointEmbeddings,
                 column_qdrant_repo: ColumnQdrantRepo,
                 value_es_repo: ValueESRepo,
                 metric_qdrant_repo: MetricQdrantRepo
                 ):

        self.meta_mysql_repo: MetaMySQLRepo = meta_mysql_repo  # MetaMySQLRepo
        self.dw_mysql_repo: DWMySQLRepo = dw_mysql_repo  # DWMySQLRepo
        self.column_qdrant_repo: ColumnQdrantRepo = column_qdrant_repo  # ColumnQdrantRepo
        self.embedding_client: HuggingFaceEndpointEmbeddings = embedding_client  # EmbeddingClient
        self.value_es_repo: ValueESRepo = value_es_repo  # ValueESRepo
        self.metric_qdrant_repo: MetricQdrantRepo = metric_qdrant_repo  # MetricQdrantRepo

    async def _save_tables_to_meta_db(self, meta_config: MetaConfig) -> list[ColumnInfo]:
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

        return column_infos

    async def _save_columns_to_qdrant(self, column_infos: list[ColumnInfo]):
        await self.column_qdrant_repo.ensure_collection()

        points: list[dict] = []
        # 这里就是将字段的name、description、alias都作为embedding_text进行向量化
        for column_info in column_infos:
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": column_info.name,
                "payload": asdict(column_info)
            })
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": column_info.description,
                "payload": asdict(column_info)
            })
            for alia in column_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "embedding_text": alia,
                    "payload": asdict(column_info)
                })

        embeddings: list[list[float]] = []
        embedding_text = [point['embedding_text'] for point in points]
        embedding_batch_size = 20  # 每批次处理的文本数量

        for i in range(0, len(embedding_text), embedding_batch_size):
            batch_texts = embedding_text[i:i + embedding_batch_size]
            batch_embedding_result = await self.embedding_client.aembed_documents(batch_texts)
            embeddings.extend(batch_embedding_result)

        ids = [point['id'] for point in points]
        payloads = [point['payload'] for point in points]

        await self.column_qdrant_repo.upsert(
            ids,
            embeddings,
            payloads
        )

    async def _save_values_to_es(self, meta_config: MetaConfig):
        await self.value_es_repo.ensure_index()

        value_infos: list[ValueInfo] = []
        for table in meta_config.tables:
            for column in table.columns:
                if column.sync:
                    current_column_values = await self.dw_mysql_repo.get_column_examples(
                        table.name,
                        column.name,
                        limit=999999
                    )
                    value_infos.extend([
                        ValueInfo(
                            id=f"{table.name}.{column.name}.{current_column_value}",
                            column_id=f"{table.name}.{column.name}",
                            value=current_column_value,
                        )
                        for current_column_value in current_column_values
                    ])

        await self.value_es_repo.index(value_infos)

    async def _save_metrics_to_meta_db(self, meta_config: MetaConfig) -> list[MetricInfo]:
        metric_infos: list[MetricInfo] = []
        column_metrics: list[ColumnMetric] = []
        for metric in meta_config.metrics:
            metric_infos.append(MetricInfo(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias
            ))
            for column in metric.relevant_columns:
                column_metrics.append(ColumnMetric(
                    metric_id=metric.name,
                    column_id=column
                ))
        async with self.meta_mysql_repo.session.begin():
            await self.meta_mysql_repo.save_metric_infos(metric_infos)
            await self.meta_mysql_repo.save_column_metrics(column_metrics)

        return metric_infos

    async def _save_metrics_to_qdrant(self, metric_infos: list[MetricInfo]):
        await self.metric_qdrant_repo.ensure_collection()

        points: list[dict] = []
        # 这里就是将字段的name、description、alias都作为embedding_text进行向量化
        for metric_info in metric_infos:
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": metric_info.name,
                "payload": asdict(metric_info)
            })
            points.append({
                "id": uuid.uuid4(),
                "embedding_text": metric_info.description,
                "payload": asdict(metric_info)
            })
            for alia in metric_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "embedding_text": alia,
                    "payload": asdict(metric_info)
                })

        embeddings: list[list[float]] = []
        embedding_text = [point['embedding_text'] for point in points]
        embedding_batch_size = 20  # 每批次处理的文本数量

        for i in range(0, len(embedding_text), embedding_batch_size):
            batch_texts = embedding_text[i:i + embedding_batch_size]
            batch_embedding_result = await self.embedding_client.aembed_documents(batch_texts)
            embeddings.extend(batch_embedding_result)

        ids = [point['id'] for point in points]
        payloads = [point['payload'] for point in points]

        await self.metric_qdrant_repo.upsert(
            ids,
            embeddings,
            payloads
        )

    async def build(self, config_path: Path):
        config_file = config_path
        context = OmegaConf.load(config_file)
        schema = OmegaConf.structured(MetaConfig)

        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        logger.info("加载元数据配置文件成功")

        # 存在表信息
        if meta_config.tables:
            # 1. 将表信息和字段信息保存到元数据库中
            column_infos = await self._save_tables_to_meta_db(meta_config)
            logger.info("保存表信息和字段信息到元数据库成功")
            # 2. 对字段信息（column_info），进行向量化，并存储到向量数据库中（qdrant）
            await self._save_columns_to_qdrant(column_infos)
            logger.info("保存字段信息到向量数据库成功")
            # 3. 对指定的维度字段，建立全文索引
            await self._save_values_to_es(meta_config)
            logger.info("保存字段取值到全文索引成功")

        # 存在指标信息
        if meta_config.metrics:
            # 1. 将指标信息存储到数据库中（metric_info, column_metric）
            metric_infos = await self._save_metrics_to_meta_db(meta_config)
            logger.info("保存指标信息到数据库成功")

            # 2. 对指标信息进行向量化，并存储到向量数据库中（qdrant）
            await self._save_metrics_to_qdrant(metric_infos)
            logger.info("保存指标信息到向量数据库成功")
