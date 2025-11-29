"""
Java服务客户端：调用Spring Cloud接口
"""
import httpx
from typing import Dict, List, Optional
from loguru import logger
from config import settings


class JavaServiceClient:
    """Java服务客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.base_url = settings.java_service_base_url
        self.api_prefix = settings.java_service_api_prefix
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )
        logger.info(f"Java服务客户端初始化，base_url: {self.base_url}")
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
    
    async def _request(self, method: str, path: str, **kwargs) -> Dict:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            path: 请求路径
            **kwargs: 其他请求参数
            
        Returns:
            响应数据
        """
        url = f"{self.api_prefix}{path}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"请求失败: {method} {url}, 错误: {e}")
            raise
    
    async def get_user_learning_profile(self, user_id: int) -> Dict:
        """
        获取用户学习画像（通过我的课表接口获取）
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户学习画像数据
        """
        # 使用 /lessons/page 接口获取用户的课表信息
        # 注意：实际接口可能需要用户认证，这里假设可以通过userId参数访问
        path = "/lessons/page"
        params = {"userId": user_id, "size": 100}  # 获取前100条
        
        data = await self._request("GET", path, params=params)
        # 返回格式：PageDTO，包含list和total
        if isinstance(data, dict):
            lessons = data.get("list", [])
            # 构建用户画像
            profile = {
                "total_courses": data.get("total", 0),
                "lessons": lessons,
                "learning_courses": [l for l in lessons if l.get("status") == 1],  # 状态1=学习中
                "finished_courses": [l for l in lessons if l.get("status") == 2],  # 状态2=已学完
            }
            return profile
        return {"lessons": data if isinstance(data, list) else []}
    
    async def get_user_purchased_courses(self, user_id: int) -> List[Dict]:
        """
        获取用户购买的课程列表（通过我的课表接口）
        
        Args:
            user_id: 用户ID
            
        Returns:
            课程列表
        """
        # 使用 /lessons/page 接口，课表即代表已购买的课程
        path = "/lessons/page"
        params = {"userId": user_id, "size": 100}
        
        data = await self._request("GET", path, params=params)
        if isinstance(data, dict):
            return data.get("list", [])
        return data if isinstance(data, list) else []
    
    async def get_user_learning_records(self, user_id: int, course_id: Optional[int] = None) -> List[Dict]:
        """
        获取用户学习记录
        
        Args:
            user_id: 用户ID
            course_id: 课程ID（可选）
            
        Returns:
            学习记录列表
        """
        if not course_id:
            # 如果没有指定课程ID，先获取用户的课表
            lessons = await self.get_user_purchased_courses(user_id)
            if not lessons:
                return []
            # 使用第一个课程作为示例，实际应该返回所有课程的学习记录
            course_id = lessons[0].get("courseId") if lessons else None
            if not course_id:
                return []
        
        # 使用 /learning-records/course/{courseId} 接口
        path = f"/learning-records/course/{course_id}"
        data = await self._request("GET", path)
        
        # 返回格式：LearningLessonDTO，包含id、latestSectionId、records
        if isinstance(data, dict):
            records = data.get("records", [])
            return records
        return data if isinstance(data, list) else []
    
    async def get_all_courses(self) -> List[Dict]:
        """
        获取所有课程（用于数据预热）
        
        Returns:
            课程列表
        """
        # 使用 /courses/page 接口分页获取所有已上架课程
        # status=2 表示已上架状态
        return await self._get_courses_by_page()
    
    async def _get_courses_by_page(self, page_size: int = 100) -> List[Dict]:
        """
        分页获取课程
        
        Args:
            page_size: 每页大小
            
        Returns:
            课程列表
        """
        all_courses = []
        page = 1
        
        while True:
            path = "/courses/page"
            params = {
                "page": page, 
                "size": page_size, 
                "status": 2  # status=2表示已上架
            }
            try:
                data = await self._request("GET", path, params=params)
                # 返回格式：PageDTO，包含list和total
                if isinstance(data, dict):
                    courses = data.get("list", [])
                    total = data.get("total", 0)
                else:
                    courses = data if isinstance(data, list) else []
                    total = len(courses)
                
                if not courses:
                    break
                
                all_courses.extend(courses)
                logger.info(f"已获取 {len(all_courses)}/{total} 门课程")
                
                # 检查是否还有更多数据
                if len(all_courses) >= total:
                    break
                
                page += 1
            except Exception as e:
                logger.error(f"分页获取课程失败: {e}")
                break
        
        return all_courses
    
    async def get_course_detail(self, course_id: int) -> Dict:
        """
        获取课程详情（包含内容和大纲）
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程详情
        """
        # 使用内部接口 /course/{id} 获取完整课程信息
        # withCatalogue=true 获取目录信息，withTeachers=false 不获取老师信息
        path = f"/course/{course_id}"
        params = {
            "withCatalogue": True,
            "withTeachers": False
        }
        
        data = await self._request("GET", path, params=params)
        
        # 如果还需要获取课程内容（介绍、详情等），可能需要额外调用
        # 这里假设返回的数据已包含基本信息
        return data

