"""
MCP工具：封装各种工具函数供Agent调用
"""
from typing import Dict, List, Optional
from loguru import logger
from services.java_client import JavaServiceClient
from rag.vector_store import VectorStore


class MCPTools:
    """MCP工具集合"""
    
    def __init__(self):
        """初始化工具"""
        self.java_client = JavaServiceClient()
        self.vector_store = VectorStore()
    
    async def get_user_learning_profile(self, user_id: int) -> Dict:
        """
        获取用户学习画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户学习画像
        """
        logger.info(f"获取用户 {user_id} 的学习画像")
        try:
            profile = await self.java_client.get_user_learning_profile(user_id)
            return profile
        except Exception as e:
            logger.error(f"获取用户画像失败: {e}")
            return {"error": str(e)}
    
    async def get_user_purchased_courses(self, user_id: int) -> List[Dict]:
        """
        获取用户购买的课程
        
        Args:
            user_id: 用户ID
            
        Returns:
            课程列表
        """
        logger.info(f"获取用户 {user_id} 购买的课程")
        try:
            courses = await self.java_client.get_user_purchased_courses(user_id)
            return courses
        except Exception as e:
            logger.error(f"获取用户课程失败: {e}")
            return []
    
    async def get_user_learning_records(self, user_id: int, course_id: Optional[int] = None) -> List[Dict]:
        """
        获取用户学习记录
        
        Args:
            user_id: 用户ID
            course_id: 课程ID（可选）
            
        Returns:
            学习记录列表
        """
        logger.info(f"获取用户 {user_id} 的学习记录")
        try:
            records = await self.java_client.get_user_learning_records(user_id, course_id)
            return records
        except Exception as e:
            logger.error(f"获取学习记录失败: {e}")
            return []
    
    async def search_courses(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        在RAG知识库中搜索相关课程
        
        Args:
            query: 搜索查询
            top_k: 返回前k个结果
            
        Returns:
            搜索结果列表
        """
        logger.info(f"搜索课程: {query}")
        try:
            results = self.vector_store.search(query, top_k=top_k)
            return results
        except Exception as e:
            logger.error(f"搜索课程失败: {e}")
            return []
    
    async def close(self):
        """关闭工具"""
        await self.java_client.close()


# 工具描述（供LangGraph使用）
TOOLS_DESCRIPTION = [
    {
        "name": "get_user_learning_profile",
        "description": "获取用户的学习画像，包括学习时长、学习习惯、学习进度等信息",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "用户ID"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_user_purchased_courses",
        "description": "获取用户购买的所有课程列表",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "用户ID"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_user_learning_records",
        "description": "获取用户的学习记录，包括学习时长、学习进度、卡点等信息",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "用户ID"
                },
                "course_id": {
                    "type": "integer",
                    "description": "课程ID（可选）"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "search_courses",
        "description": "在课程知识库中搜索相关课程，用于推荐和匹配",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询文本"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回前k个结果，默认5"
                }
            },
            "required": ["query"]
        }
    }
]

