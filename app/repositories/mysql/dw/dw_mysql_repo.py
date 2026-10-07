# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 14:20
# @Author : KarryLiu
# File : dw_mysql_repo
# @Project : data_agent
from sqlalchemy import text

from app.core.log import logger


class DWMySQLRepo:
    def __init__(self, session):
        self.session = session  # MySQL session

    def read(self):
        pass

    def write(self):
        pass

    async def get_column_types(self, table_name):
        sql = f"show columns from {table_name};"
        result = await self.session.execute(text(sql))
        result_dict = result.mappings().fetchall()
        return {row['Field']: row['Type'] for row in result_dict}

    async def get_column_examples(self, table_name, col_name, limit=10):
        sql = f"select distinct {col_name} from {table_name} limit {limit};"
        result = await self.session.execute(text(sql))
        result_dict = result.fetchall()
        return [row[0] for row in result_dict]
        # result_dict = result.mappings().fetchall()
        # return [row[col_name] for row in result_dict]

    async def get_db_info(self):
        sql = "select VERSION();"
        result = await self.session.execute(text(sql))
        version = result.scalar()

        dialect = self.session.bind.dialect.name  # 获取数据库类型

        return {
            "dialect": dialect,
            "version": version
        }

    async def validate_sql(self, sql):
        sql = f"explain {sql}"
        try:
            await self.session.execute(text(sql))
            logger.info(f"SQL语句验证成功")
            return {"error": None}
        except Exception as e:
            logger.error(f"SQL语句验证失败: {str(e)}")
            return {"error": str(e)}

    async def run_sql(self, sql) -> list[dict]:
        result = await self.session.execute(text(sql))
        return [dict(row) for row in result.mappings().fetchall()]
