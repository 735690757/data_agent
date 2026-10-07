# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:49
# @Author : KarryLiu
# File : validate_sql
# @Project : data_agent
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "验证SQL语句", "status": "running"})
    try:
        sql = state["sql"]

        dw_mysql_repo = runtime.context["dw_mysql_repo"]
        try:
            await dw_mysql_repo.validate_sql(sql)
            writer({"type": "progress", "step": "验证SQL语句", "status": "success"})
            return {"error": None}
        except Exception as e:
            logger.error(f"SQL语句验证失败: {e}")
            writer({"type": "progress", "step": "验证SQL语句", "status": "success"})
            return {"error": str(e)}

    except Exception as e:
        logger.error(f"验证SQL语句失败: {e}")
        writer({"type": "progress", "step": "验证SQL语句", "status": "error"})
        raise e
