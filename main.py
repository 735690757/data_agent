# _*_ coding : utf-8 _*_
# @Time : 2026/9/18 10:57
# @Author : KarryLiu
# File : main
# @Project : data_agent
import uuid

from fastapi import FastAPI, Request

from app.api.life_span import lifespan
from app.api.routers.query_router import query_router
from app.core.context import request_id_ctx_var

app = FastAPI(lifespan=lifespan)

app.include_router(router=query_router, tags=["Data Agent"])



@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = uuid.uuid4()
    request_id_ctx_var.set(request_id)
    response = await call_next(request)
    return response
