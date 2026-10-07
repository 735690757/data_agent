# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:19
# @Author : KarryLiu
# File : filter_table
# @Project : data_agent
import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, TableInfoState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤表", "status": "running"})
    try:
        query: str = state["query"]
        table_infos: list[TableInfoState] = state["table_infos"]

        prompt = PromptTemplate(
            template=load_prompt("filter_table_info"),
            input_variables=['query', 'table_infos'],
        )

        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({
            "query": query,
            "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False)
        })
        filtered_table_infos: list[TableInfoState] = []

        for table_info in table_infos:
            if table_info["name"] in result:
                table_info["columns"] = [column_info for column_info in table_info["columns"] if
                                         column_info["name"] in result[table_info["name"]]]
                filtered_table_infos.append(table_info)

        logger.info(f"过滤后的表信息: {[filtered_table_info['name'] for filtered_table_info in filtered_table_infos]}")
        writer({"type": "progress", "step": "过滤表", "status": "success"})
        return {
            "table_infos": filtered_table_infos
        }
    except Exception as e:
        logger.error(f"过滤表失败: {e}")
        writer({"type": "progress", "step": "过滤表", "status": "error"})
        raise e
