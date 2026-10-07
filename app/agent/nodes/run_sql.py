# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:20
# @Author : KarryLiu
# File : run_sql
# @Project : data_agent
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def run_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "运行SQL语句", "status": "running"})
    try:
        sql = state["sql"]
        dw_mysql_repo = runtime.context["dw_mysql_repo"]

        result = await dw_mysql_repo.run_sql(sql)

        logger.info(f"运行SQL语句结果: {result}")
        writer({"type": "progress", "step": "运行SQL语句", "status": "success"})
        writer({"type": "result", "data": result})
    except Exception as e:
        logger.error(f"运行SQL语句失败: {e}")
        writer({"type": "progress", "step": "运行SQL语句", "status": "error"})
        raise e
