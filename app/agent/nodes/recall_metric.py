# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:18
# @Author : KarryLiu
# File : recall_metric
# @Project : data_agent
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.metric_info import MetricInfo
from app.prompt.prompt_loader import load_prompt


async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回指标", "status": "running"})
    try:
        query = state["query"]
        keywords = state["keywords"]
        embedding_client = runtime.context["embedding_client"]
        metric_qdrant_repo = runtime.context["metric_qdrant_repo"]

        # 借助LLM扩展关键词
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_metric_recall"),
            input_variables=['query'],
        )

        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({
            "query": query,
        })
        logger.info(f"LLM扩展关键词结果: {result}")
        keywords = set(keywords + result)

        # 召回指标，有可能被多次召回，所以需要去重这里用map做
        metric_infos_map: dict[str, MetricInfo] = {}
        for keyword in keywords:
            # 对keyword进行向量化
            embedding_vector = await embedding_client.aembed_query(keyword)
            # 在qdrant中召回列
            current_metric_infos: list[MetricInfo] = await metric_qdrant_repo.search(
                embedding_vector,
                score_threshold=0.6,
                limit=10
            )
            for current_metric_info in current_metric_infos:
                if current_metric_info.id not in metric_infos_map:
                    metric_infos_map[current_metric_info.id] = current_metric_info

        retrieve_metric_infos: list[MetricInfo] = list(metric_infos_map.values())

        logger.info(f"召回指标的ID: {list(metric_infos_map.keys())}")
        writer({"type": "progress", "step": "召回指标", "status": "success"})
        return {"retrieve_metric_infos": retrieve_metric_infos}
    except Exception as e:
        logger.error(f"召回指标失败: {e}")
        writer({"type": "progress", "step": "召回指标", "status": "error"})
        raise e
