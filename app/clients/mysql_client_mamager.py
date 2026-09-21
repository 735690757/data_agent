# _*_ coding : utf-8 _*_
# @Time : 2026/9/17 20:19
# @Author : KarryLiu
# File : mysql_client_mamager
# @Project : data_agent
import asyncio

from sqlalchemy import text, URL

from app.conf.app_config import DBConfig, app_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker


class MySQLClientManager:
    def __init__(self, config: DBConfig):
        self.engine: AsyncEngine | None = None
        self.session_factory = None
        self.config = config

    def _get_url(self):
        return URL.create(
            drivername="mysql+asyncmy",
            username=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            query={"charset": "utf8mb4"}
        )

    def init(self):
        self.engine = create_async_engine(
            self._get_url(),
            pool_size=50,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=True
        )

    async def close(self):
        await self.engine.dispose()


meta_mysql_client_manager = MySQLClientManager(app_config.db_meta)
dw_mysql_client_manager = MySQLClientManager(app_config.db_dw)

if __name__ == '__main__':
    dw_mysql_client_manager.init()

    dw_engine = dw_mysql_client_manager.engine


    async def test():
        async with dw_mysql_client_manager.session_factory() as session:
            sql = "select * from fact_order"
            result = await session.execute(text(sql))
            result.mappings()
            rows = result.fetchall()
            print(rows)
            print("-----------")
            print(rows[0])
            print(f"Total rows: {len(rows)}")
            print(rows[0].region_id)


    asyncio.run(test())
