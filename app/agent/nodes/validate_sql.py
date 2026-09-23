# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:49
# @Author : KarryLiu
# File : validate_sql
# @Project : data_agent
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer("验证SQL语句")
    import asyncio
    await asyncio.sleep(0.5)
