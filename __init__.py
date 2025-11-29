"""
Tianji AI Assistant

基于 MCP + LLM + RAG 的个性化课程推荐助手

主要模块：
- agent: LangGraph Agent编排和MCP工具
- rag: 向量数据库和嵌入模型
- services: Java服务客户端和数据同步
- config: 配置管理

快速开始：
    from agent import CourseRecommendationAgent
    from config import settings
    
    # 初始化Agent
    agent = CourseRecommendationAgent()
    
    # 执行对话
    answer = await agent.invoke(
        user_id=123,
        query="我学Java多线程很吃力，接下来咋办？"
    )
"""

__version__ = "1.0.0"
__author__ = "Tianji Team"

# 导出主要类和函数
from config import settings

__all__ = [
    "settings",
]

