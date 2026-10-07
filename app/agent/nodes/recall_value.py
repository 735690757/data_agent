# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:18
# @Author : KarryLiu
# File : recall_value
# @Project : data_agent
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.value_info import ValueInfo
from app.prompt.prompt_loader import load_prompt


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    from langgraph.config import get_stream_writer
    writer = get_stream_writer()
    writer({"type": "progress", "step": "召回字段取值", "status": "running"})
    try:
        query = state["query"]
        keywords = state["keywords"]
        value_es_repo = runtime.context["value_es_repo"]

        # 扩展关键词
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_value_recall"),
            input_variables=['query'],
        )

        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({
            "query": query,
        })
        logger.info(f"LLM扩展关键词结果: {result}")
        keywords = set(keywords + result)

        # 召回字段取值
        value_infos_map: dict[str, ValueInfo] = {}

        for keyword in keywords:
            current_value_infos: list[ValueInfo] = await value_es_repo.search(
                keyword,
                score_threshold=0.6,
                limit=10
            )
            for current_value_info in current_value_infos:
                if current_value_info.id not in value_infos_map:
                    value_infos_map[current_value_info.id] = current_value_info

        retrieve_value_infos: list[ValueInfo] = list(value_infos_map.values())
        logger.info(f"召回字段取值的ID: {list(value_infos_map.keys())}")
        writer({"type": "progress", "step": "召回字段取值", "status": "success"})
        return {"retrieve_value_infos": retrieve_value_infos}
    except Exception as e:
        logger.error(f"召回字段取值失败: {e}")
        writer({"type": "progress", "step": "召回字段取值", "status": "error"})
        raise e
