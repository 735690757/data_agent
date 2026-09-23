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
from app.entities.table_info import TableInfo
from app.repositories.es.value_es_repo import ValueESRepo
from app.repositories.mysql.dw.dw_mysql_repo import DWMySQLRepo
from app.repositories.mysql.meta.meta_mysql_repo import MetaMySQLRepo
from app.repositories.qdrant.column_qdrant_repo import ColumnQdrantRepo


class MetaKnowledgeService:
    def __init__(self, meta_mysql_repo: MetaMySQLRepo,
                 dw_mysql_repo: DWMySQLRepo,
                 embedding_client: HuggingFaceEndpointEmbeddings,
                 column_qdrant_repo: ColumnQdrantRepo,
                 value_es_repo: ValueESRepo):

        self.meta_mysql_repo: MetaMySQLRepo = meta_mysql_repo  # MetaMySQLRepo
        self.dw_mysql_repo: DWMySQLRepo = dw_mysql_repo  # DWMySQLRepo
        self.column_qdrant_repo: ColumnQdrantRepo = column_qdrant_repo  # ColumnQdrantRepo
        self.embedding_client: HuggingFaceEndpointEmbeddings = embedding_client  # EmbeddingClient
        self.value_es_repo: ValueESRepo = value_es_repo  # ValueESRepo

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

            # 3. 对指定的维度字段，建立全文索引
            await self.value_es_repo.ensure_index()









        # 存在指标信息
        if meta_config.metrics:
            # 1. 将指标信息存储到数据库中（metric_info, column_metric）

            # 2. 对指标信息进行向量化，并存储到向量数据库中（qdrant）
            pass
