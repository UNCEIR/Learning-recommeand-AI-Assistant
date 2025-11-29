"""
FastAPI主服务：提供HTTP接口和生命周期管理
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from loguru import logger
import sys

from config import settings
from services.data_sync import DataSyncService
from rag.vector_store import VectorStore
from agent.graph import CourseRecommendationAgent


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level
)


# 全局变量
agent: Optional[CourseRecommendationAgent] = None
vector_store: Optional[VectorStore] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在启动时自动同步数据，关闭时清理资源
    """
    global agent, vector_store
    
    # ========== 启动阶段 ==========
    logger.info("=" * 60)
    logger.info("Python AI服务启动中...")
    logger.info("=" * 60)
    
    # 初始化向量数据库
    logger.info("初始化向量数据库...")
    vector_store = VectorStore()
    
    # 检查知识库是否为空
    current_count = vector_store.count()
    logger.info(f"当前知识库文档数量: {current_count}")
    
    if current_count == 0:
        logger.warning("检测到知识库为空，开始从Java端同步数据...")
        try:
            # 执行数据同步
            sync_service = DataSyncService()
            synced_count = await sync_service.sync_all_courses()
            
            if synced_count > 0:
                logger.success(f"数据预热完成！共导入 {synced_count} 门课程数据。")
            else:
                logger.warning("数据同步完成，但未导入任何数据。")
            
            await sync_service.close()
        except Exception as e:
            logger.error(f"数据同步失败: {e}")
            logger.warning("服务将继续启动，但知识库为空，可能影响推荐功能。")
    else:
        logger.info(f"知识库状态正常，包含 {current_count} 条数据。")
    
    # 初始化Agent
    logger.info("初始化AI Agent...")
    try:
        agent = CourseRecommendationAgent()
        logger.success("AI Agent初始化完成")
    except Exception as e:
        logger.error(f"AI Agent初始化失败: {e}")
        logger.warning("服务将继续启动，但AI功能可能不可用。")
    
    logger.info("=" * 60)
    logger.success("服务启动完成，开始接收请求")
    logger.info("=" * 60)
    
    yield  # 服务运行中
    
    # ========== 关闭阶段 ==========
    logger.info("服务正在关闭...")
    if agent:
        await agent.close()
    logger.info("服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Tianji AI Assistant",
    description="个性化课程推荐助手 - MCP + LLM + RAG",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 请求模型 ==========
class ChatRequest(BaseModel):
    """聊天请求"""
    user_id: int
    query: str
    context: Optional[Dict] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str
    user_id: int


class SyncRequest(BaseModel):
    """数据同步请求"""
    force: bool = False  # 是否强制同步（清空后重新同步）


class SyncResponse(BaseModel):
    """数据同步响应"""
    success: bool
    message: str
    synced_count: int


# ========== API接口 ==========
@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Tianji AI Assistant",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    global agent, vector_store
    
    status = {
        "status": "healthy",
        "vector_store": {
            "initialized": vector_store is not None,
            "document_count": vector_store.count() if vector_store else 0
        },
        "agent": {
            "initialized": agent is not None
        }
    }
    
    return status


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口：接收用户查询，返回AI回复
    
    Args:
        request: 聊天请求
        
    Returns:
        AI回复
    """
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="AI Agent未初始化")
    
    try:
        logger.info(f"收到用户 {request.user_id} 的查询: {request.query}")
        
        # 调用Agent
        answer = await agent.invoke(
            user_id=request.user_id,
            query=request.query,
            context=request.context
        )
        
        logger.info(f"生成回复完成，长度: {len(answer)}")
        
        return ChatResponse(
            answer=answer,
            user_id=request.user_id
        )
    except Exception as e:
        logger.error(f"处理聊天请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


@app.post("/sync", response_model=SyncResponse)
async def sync_data(request: SyncRequest):
    """
    手动触发数据同步
    
    Args:
        request: 同步请求
        
    Returns:
        同步结果
    """
    global vector_store
    
    if not vector_store:
        raise HTTPException(status_code=503, detail="向量数据库未初始化")
    
    try:
        logger.info("开始手动数据同步...")
        
        # 如果强制同步，先清空
        if request.force:
            logger.info("强制同步模式：清空现有数据...")
            vector_store.reset()
        
        # 执行同步
        sync_service = DataSyncService()
        synced_count = await sync_service.sync_all_courses()
        await sync_service.close()
        
        logger.success(f"数据同步完成，共同步 {synced_count} 门课程")
        
        return SyncResponse(
            success=True,
            message=f"成功同步 {synced_count} 门课程",
            synced_count=synced_count
        )
    except Exception as e:
        logger.error(f"数据同步失败: {e}")
        return SyncResponse(
            success=False,
            message=f"同步失败: {str(e)}",
            synced_count=0
        )


@app.get("/stats")
async def get_stats():
    """获取统计信息"""
    global vector_store
    
    stats = {
        "vector_store": {
            "document_count": vector_store.count() if vector_store else 0
        }
    }
    
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True
    )

