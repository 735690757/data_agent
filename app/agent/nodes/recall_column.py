# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:18
# @Author : KarryLiu
# File : recall_column
# @Project : data_agent
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger


async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回列", "status": "running"})
    try:
        query = state["query"]
        keywords = state["keywords"]
        column_qdrant_repo = runtime.context["column_qdrant_repo"]
        embedding_client = runtime.context["embedding_client"]

        # 让LLM扩展关键词
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_column_recall"),
            input_variables=['query'],
        )

        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({
            "query": query,
        })
        logger.info(f"LLM扩展关键词结果: {result}")
        keywords = set(keywords + result)

        # 召回列，有可能被多次召回，所以需要去重这里用map做
        column_infos_map: dict[str, ColumnInfo] = {}
        for keyword in keywords:
            # 对keyword进行向量化
            embedding_vector = await embedding_client.aembed_query(keyword)
            # 在qdrant中召回列
            """
            返回的应该是 Payload
            {
                "id":"dim_customer.gender"
                "name":"gender"
                "type":"varchar(10)"
                "role":"dimension"
                "examples":[
                    0:"男"
                    1:"女"
                ]
                "description":"客户性别。"
                "alias":[
                    0:"性别"
                ]
                "table_id":"dim_customer"
            }
            """
            current_column_infos: list[ColumnInfo] = await column_qdrant_repo.search(
                embedding_vector,
                score_threshold=0.6,
                limit=10
            )
            for current_column_info in current_column_infos:
                if current_column_info.id not in column_infos_map:
                    column_infos_map[current_column_info.id] = current_column_info

        retrieve_column_infos: list[ColumnInfo] = list(column_infos_map.values())

        logger.info(f"召回列的ID: {list(column_infos_map.keys())}")
        writer({"type": "progress", "step": "召回列", "status": "success"})
        return {"retrieve_column_infos": retrieve_column_infos}
    except Exception as e:
        logger.error(f"召回列失败: {e}")
        writer({"type": "progress", "step": "召回列", "status": "error"})
        raise e
