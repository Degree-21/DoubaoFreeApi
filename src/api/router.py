from fastapi import APIRouter
from .endpoints import chat
from .endpoints import file
from .endpoints import session

router = APIRouter()

# 注册各个模块的路由
router.include_router(chat.router, prefix="/chat", tags=["聊天"])
router.include_router(file.router, prefix="/file", tags=["文件"])
router.include_router(session.router, prefix="/session", tags=["会话配置"])