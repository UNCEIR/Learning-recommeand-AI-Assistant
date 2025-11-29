"""
数据同步服务：从Java端同步课程数据到RAG知识库
"""
from typing import List, Dict
from loguru import logger
from services.java_client import JavaServiceClient
from rag.vector_store import VectorStore


class DataSyncService:
    """数据同步服务"""
    
    def __init__(self):
        """初始化服务"""
        self.java_client = JavaServiceClient()
        self.vector_store = VectorStore()
    
    async def sync_all_courses(self) -> int:
        """
        同步所有课程到RAG知识库
        
        Returns:
            同步的课程数量
        """
        logger.info("开始从Java端同步课程数据...")
        
        try:
            # 1. 获取所有课程
            courses = await self.java_client.get_all_courses()
            logger.info(f"从Java端获取到 {len(courses)} 门课程")
            
            if not courses:
                logger.warning("未获取到任何课程数据")
                return 0
            
            # 2. 获取每门课程的详细信息
            documents = []
            for course in courses:
                try:
                    course_id = course.get("id")
                    if not course_id:
                        continue
                    
                    # 获取课程详情（包含内容和大纲）
                    course_detail = await self.java_client.get_course_detail(course_id)
                    
                    # 构建文档文本
                    doc_text = self._build_course_document(course, course_detail)
                    
                    # 构建元数据
                    metadata = {
                        "course_id": str(course_id),
                        "course_name": course.get("name", ""),
                        "course_type": str(course.get("courseType", "")),
                        "category": self._get_category_path(course),
                        "price": str(course.get("price", 0)),
                        "status": str(course.get("status", ""))
                    }
                    
                    documents.append({
                        "id": f"course_{course_id}",
                        "text": doc_text,
                        "metadata": metadata
                    })
                    
                    logger.debug(f"已处理课程: {course.get('name', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"处理课程 {course.get('id')} 时出错: {e}")
                    continue
            
            # 3. 批量添加到向量数据库
            if documents:
                self.vector_store.add_documents(documents)
                logger.info(f"成功同步 {len(documents)} 门课程到RAG知识库")
                return len(documents)
            else:
                logger.warning("没有可同步的文档")
                return 0
                
        except Exception as e:
            logger.error(f"同步课程数据失败: {e}")
            raise
        finally:
            await self.java_client.close()
    
    def _build_course_document(self, course: Dict, course_detail: Dict) -> str:
        """
        构建课程文档文本
        
        Args:
            course: 课程基本信息
            course_detail: 课程详细信息
            
        Returns:
            文档文本
        """
        parts = []
        
        # 课程名称
        if course.get("name"):
            parts.append(f"课程名称：{course['name']}")
        
        # 课程介绍
        if course_detail.get("courseIntroduce"):
            parts.append(f"课程介绍：{course_detail['courseIntroduce']}")
        
        # 适用人群
        if course_detail.get("usePeople"):
            parts.append(f"适用人群：{course_detail['usePeople']}")
        
        # 课程详情
        if course_detail.get("courseDetail"):
            parts.append(f"课程详情：{course_detail['courseDetail']}")
        
        # 课程分类
        category_path = self._get_category_path(course)
        if category_path:
            parts.append(f"课程分类：{category_path}")
        
        # 课程类型
        course_type = course.get("courseType")
        if course_type:
            type_name = "直播课" if course_type == 1 else "录播课"
            parts.append(f"课程类型：{type_name}")
        
        # 课程大纲（从course_detail中获取，如果有catalogue信息）
        if course_detail.get("catalogue"):
            parts.append("课程大纲：")
            catalogue_text = self._format_catalogue(course_detail["catalogue"])
            parts.append(catalogue_text)
        
        return "\n".join(parts)
    
    def _get_category_path(self, course: Dict) -> str:
        """
        获取课程分类路径
        
        Args:
            course: 课程信息
            
        Returns:
            分类路径字符串
        """
        # 这里需要根据实际的分类数据结构调整
        # 假设有firstCateName, secondCateName, thirdCateName字段
        categories = []
        if course.get("firstCateName"):
            categories.append(course["firstCateName"])
        if course.get("secondCateName"):
            categories.append(course["secondCateName"])
        if course.get("thirdCateName"):
            categories.append(course["thirdCateName"])
        
        return " > ".join(categories) if categories else ""
    
    def _format_catalogue(self, catalogue: List[Dict]) -> str:
        """
        格式化课程大纲
        
        Args:
            catalogue: 大纲列表
            
        Returns:
            格式化后的大纲文本
        """
        if not catalogue:
            return ""
        
        lines = []
        for item in catalogue:
            name = item.get("name", "")
            item_type = item.get("type", 1)
            type_name = {1: "章", 2: "节", 3: "测试"}.get(item_type, "未知")
            
            # 根据层级添加缩进
            level = item.get("level", 0)
            indent = "  " * level
            lines.append(f"{indent}{type_name}：{name}")
            
            # 如果有子项，递归处理
            if item.get("children"):
                children_text = self._format_catalogue(item["children"])
                lines.append(children_text)
        
        return "\n".join(lines)
    
    async def close(self):
        """关闭服务"""
        await self.java_client.close()

