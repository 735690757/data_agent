# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:19
# @Author : KarryLiu
# File : merge_retrieved_info
# @Project : data_agent
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("合并检索信息")
    import asyncio
    await asyncio.sleep(0.5)
