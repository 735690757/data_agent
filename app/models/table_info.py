# _*_ coding : utf-8 _*_
# @Time : 2026/9/21 13:34
# @Author : KarryLiu
# File : table_info
# @Project : data_agent
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class TableInfoMySQL(Base):
    __tablename__ = "table_info"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        comment="表编号"
    )
    name: Mapped[str | None] = mapped_column(
        String(128),
        comment="表名称"
    )
    role: Mapped[str | None] = mapped_column(
        String(32),
        comment="表类型(fact/dim)"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        comment="表描述"
    )

    def __repr__(self):
        return f"<TableInfoMySQL(id={self.id}, name={self.name}, role={self.role}, description={self.description})>"

