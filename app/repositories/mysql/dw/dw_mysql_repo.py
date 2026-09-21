# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 14:20
# @Author : KarryLiu
# File : dw_mysql_repo
# @Project : data_agent
from sqlalchemy import text


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

    async def get_column_examples(self, table_name, col_name):
        sql = f"select distinct {col_name} from {table_name} limit 10;"
        result = await self.session.execute(text(sql))
        result_dict = result.fetchall()
        return [row[0] for row in result_dict]
        # result_dict = result.mappings().fetchall()
        # return [row[col_name] for row in result_dict]
