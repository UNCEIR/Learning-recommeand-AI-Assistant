"""
嵌入模型封装
"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from config import settings
from loguru import logger


class EmbeddingModel:
    """嵌入模型封装类"""
    
    def __init__(self, model_name: str = None):
        """
        初始化嵌入模型
        
        Args:
            model_name: 模型名称，默认使用配置中的模型
        """
        self.model_name = model_name or settings.embedding_model
        logger.info(f"正在加载嵌入模型: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info("嵌入模型加载完成")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        将文档列表转换为向量
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """
        将查询文本转换为向量
        
        Args:
            text: 查询文本
            
        Returns:
            向量
        """
        embedding = self.model.encode([text])
        return embedding[0].tolist()
    
    @property
    def dimension(self) -> int:
        """获取向量维度"""
        # 使用一个测试文本获取维度
        test_embedding = self.embed_query("test")
        return len(test_embedding)

