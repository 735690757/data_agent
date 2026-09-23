# _*_ coding : utf-8 _*_
# @Time : 2026/9/23 19:37
# @Author : KarryLiu
# File : llm
# @Project : data_agent
from langchain.chat_models import init_chat_model

from app.conf.app_config import app_config

llm = init_chat_model(
    model=app_config.llm.model_name,
    api_key=app_config.llm.api_key,
    model_provider="openai",
    base_url=app_config.llm.base_url,
    temperature=0,
)

if __name__ == '__main__':
    print(llm.invoke("你好，你是谁？").content)