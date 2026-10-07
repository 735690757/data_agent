# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 15:19
# @Author : KarryLiu
# File : add_extra_context
# @Project : data_agent
from datetime import date

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DBInfoState
from app.core.log import logger


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "添加额外上下文信息", "status": "running"})
    try:
        dw_mysql_repo = runtime.context["dw_mysql_repo"]

        # 获取DateInfo
        today = date.today()
        date_str = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = f"Q{(today.month - 1) // 3 + 1}"
        date_info = DateInfoState(date=date_str, weekday=weekday, quarter=quarter)

        db = await dw_mysql_repo.get_db_info()

        db_info = DBInfoState(**db)

        logger.info(f"添加的额外上下文信息: date_info={date_info}, db_info={db_info}")
        writer({"type": "progress", "step": "添加额外上下文信息", "status": "success"})
        return {
            "date_info": date_info,
            "db_info": db_info
        }
    except Exception as e:
        logger.error(f"添加额外上下文信息失败: {e}")
        writer({"type": "progress", "step": "添加额外上下文信息", "status": "error"})
        raise e
