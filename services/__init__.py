"""
服务层：Java客户端和数据同步

本模块提供与Java服务的交互功能，包括：
- JavaServiceClient: Java服务HTTP客户端（调用Spring Cloud接口）
- DataSyncService: 数据同步服务（从Java端同步课程数据到RAG知识库）

使用示例：
    from services import JavaServiceClient, DataSyncService
    
    # 初始化Java客户端
    java_client = JavaServiceClient()
    
    # 获取用户课表
    courses = await java_client.get_user_purchased_courses(user_id=123)
    
    # 数据同步
    sync_service = DataSyncService()
    count = await sync_service.sync_all_courses()
    
    # 记得关闭客户端
    await java_client.close()
"""

from services.java_client import JavaServiceClient
from services.data_sync import DataSyncService

__version__ = "1.0.0"
__all__ = [
    "JavaServiceClient",
    "DataSyncService",
]

