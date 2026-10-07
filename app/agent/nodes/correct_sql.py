# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:20
# @Author : KarryLiu
# File : correct_sql
# @Project : data_agent
import yaml
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "纠正SQL语句", "status": "running"})
    try:
        query = state["query"]
        table_info = state["table_infos"]
        metric_infos = state["metric_infos"]
        date_info = state["date_info"]
        db_info = state["db_info"]
        sql = state["sql"]
        error = state["error"]

        prompt = PromptTemplate(
            template=load_prompt("correct_sql"),
            input_variables=['query', 'table_infos', 'metric_infos', 'date_info', 'db_info', 'error']
        )

        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({
            "query": query,
            "table_infos": yaml.dump(table_info, allow_unicode=True, sort_keys=False),
            "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
            "date_info": yaml.dump(date_info, allow_unicode=True, sort_keys=False),
            "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False),
            "sql": sql,
            "error": error,
        })
        logger.info(f"纠正后的SQL语句: {result}")
        writer({"type": "progress", "step": "纠正SQL语句", "status": "success"})
        return {
            "sql": result
        }
    except Exception as e:
        logger.error(f"纠正SQL语句失败: {e}")
        writer({"type": "progress", "step": "纠正SQL语句", "status": "error"})
        raise e
