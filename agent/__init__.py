"""
Agent模块：LangGraph编排和MCP工具

本模块提供智能对话Agent，包括：
- CourseRecommendationAgent: 课程推荐Agent（基于LangGraph）
- MCPTools: MCP工具集合（封装Java接口调用和RAG检索）
- TOOLS_DESCRIPTION: 工具描述（供LangGraph使用）

使用示例：
    from agent import CourseRecommendationAgent, MCPTools
    
    # 初始化Agent
    agent = CourseRecommendationAgent()
    
    # 执行对话
    answer = await agent.invoke(
        user_id=123,
        query="我学Java多线程很吃力，接下来咋办？"
    )
    
    # 使用工具
    tools = MCPTools()
    profile = await tools.get_user_learning_profile(user_id=123)
"""

from agent.graph import CourseRecommendationAgent
from agent.tools import MCPTools, TOOLS_DESCRIPTION

__version__ = "1.0.0"
__all__ = [
    "CourseRecommendationAgent",
    "MCPTools",
    "TOOLS_DESCRIPTION",
]

