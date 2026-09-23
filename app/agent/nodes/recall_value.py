# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:18
# @Author : KarryLiu
# File : recall_value
# @Project : data_agent
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    from langgraph.config import get_stream_writer
    writer = get_stream_writer()
    writer("召回值")
    import asyncio
    await asyncio.sleep(0.5)
