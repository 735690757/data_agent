# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:19
# @Author : KarryLiu
# File : filter_metric
# @Project : data_agent
import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState, MetricInfoState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤指标", "status": "running"})
    try:
        query: str = state["query"]
        metric_infos: list[MetricInfoState] = state["metric_infos"]

        prompt = PromptTemplate(
            template=load_prompt("filter_metric_info"),
            input_variables=['query', 'metric_infos'],
        )

        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({
            "query": query,
            "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
        })

        filter_metric_infos = [metric_info for metric_info in metric_infos if metric_info["name"] in result]

        logger.info(f"过滤后的指标: {[metric_info['name'] for metric_info in filter_metric_infos]}")
        writer({"type": "progress", "step": "过滤指标", "status": "success"})
        return {"metric_infos": filter_metric_infos}
    except Exception as e:
        logger.error(f"过滤指标失败: {e}")
        writer({"type": "progress", "step": "过滤指标", "status": "error"})
        raise e
