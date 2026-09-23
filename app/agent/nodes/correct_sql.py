# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:20
# @Author : KarryLiu
# File : correct_sql
# @Project : data_agent
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("纠正SQL语句")
    import asyncio
    await asyncio.sleep(0.5)
