# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:19
# @Author : KarryLiu
# File : merge_retrieved_info
# @Project : data_agent
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, TableInfoState, ColumnInfoState, MetricInfoState
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.core.log import logger


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "合并检索信息", "status": "running"})
    try:
        retrieve_column_infos: list[ColumnInfo] = state["retrieve_column_infos"]
        retrieve_metric_infos: list[MetricInfo] = state["retrieve_metric_infos"]
        retrieve_value_infos: list[ValueInfo] = state["retrieve_value_infos"]

        meta_mysql_repo = runtime.context["meta_mysql_repo"]

        # 处理表信息
        retrieve_column_infos_map: dict[str, ColumnInfo] = {column_info.id: column_info for column_info in
                                                            retrieve_column_infos}
        for retrieve_metric_info in retrieve_metric_infos:
            for relevant_column_id in retrieve_metric_info.relevant_columns:
                if relevant_column_id not in retrieve_column_infos_map:
                    column_info: ColumnInfo = await meta_mysql_repo.get_column_info_by_id(relevant_column_id)
                    retrieve_column_infos_map[relevant_column_id] = column_info

        # 将字段加入到其所属的examples中
        for retrieve_value_info in retrieve_value_infos:
            value = retrieve_value_info.value
            column_id = retrieve_value_info.column_id
            if column_id not in retrieve_column_infos_map:
                column_info: ColumnInfo = await meta_mysql_repo.get_column_info_by_id(column_id)
                retrieve_column_infos_map[column_id] = column_info
            if value not in retrieve_column_infos_map[column_id].examples:
                retrieve_column_infos_map[column_id].examples.append(value)

        # 将字段按照所属表进行分组
        table_to_columns_map: dict[str, list[ColumnInfo]] = {}
        for column_info in retrieve_column_infos_map.values():
            table_id = column_info.table_id
            if table_id not in table_to_columns_map:
                table_to_columns_map[table_id] = []
            table_to_columns_map[table_id].append(column_info)

        # 强制为每个表添加一个主外键字段
        for table_id in table_to_columns_map.keys():
            key_columns: list[ColumnInfo] = await meta_mysql_repo.get_key_columns_by_tabele_id(table_id)
            column_ids = [column_info.id for column_info in table_to_columns_map[table_id]]
            for key_column in key_columns:
                if key_column not in column_ids:
                    table_to_columns_map[table_id].append(key_column)

        tables_infos: list[TableInfoState] = []
        for table_id, column_infos in table_to_columns_map.items():
            table_info: TableInfo = await meta_mysql_repo.get_table_info_by_id(table_id)
            columns = [ColumnInfoState(
                name=column_info.name,
                type=column_info.type,
                role=column_info.role,
                description=column_info.description,
                examples=column_info.examples,
                alias=column_info.alias
            ) for column_info in column_infos]
            table_info_state = TableInfoState(
                name=table_info.name,
                role=table_info.role,
                description=table_info.description,
                columns=columns
            )
            tables_infos.append(table_info_state)

        # 处理指标信息
        metrics_infos: list[MetricInfoState] = [MetricInfoState(
            name=retrieve_metric_info.name,
            description=retrieve_metric_info.description,
            relevant_columns=retrieve_metric_info.relevant_columns,
            alias=retrieve_metric_info.alias
        ) for retrieve_metric_info in retrieve_metric_infos]

        writer({"type": "progress", "step": "合并检索信息", "status": "success"})
        return {
            "table_infos": tables_infos,
            "metric_infos": metrics_infos
        }
    except Exception as e:
        logger.error(f"合并检索信息失败: {e}")
        writer({"type": "progress", "step": "合并检索信息", "status": "error"})
        raise e
