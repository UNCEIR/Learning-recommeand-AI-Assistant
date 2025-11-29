"""
向量数据库封装（ChromaDB）
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from loguru import logger
import os
from config import settings
from rag.embedding import EmbeddingModel


class VectorStore:
    """向量数据库封装类"""
    
    def __init__(self, collection_name: str = "courses"):
        """
        初始化向量数据库
        
        Args:
            collection_name: 集合名称
        """
        self.collection_name = collection_name
        self.db_path = settings.chroma_db_path
        
        # 确保目录存在
        os.makedirs(self.db_path, exist_ok=True)
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # 初始化嵌入模型
        self.embedding_model = EmbeddingModel()
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        
        logger.info(f"向量数据库初始化完成，集合: {self.collection_name}")
    
    def add_documents(self, documents: List[Dict[str, str]], batch_size: int = 100):
        """
        批量添加文档到向量数据库
        
        Args:
            documents: 文档列表，每个文档包含 id, text, metadata
            batch_size: 批次大小
        """
        if not documents:
            logger.warning("文档列表为空，跳过添加")
            return
        
        total = len(documents)
        logger.info(f"开始添加 {total} 个文档到向量数据库...")
        
        # 提取文本
        texts = [doc["text"] for doc in documents]
        ids = [doc["id"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        
        # 批量处理
        for i in range(0, total, batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            
            # 生成嵌入向量
            embeddings = self.embedding_model.embed_documents(batch_texts)
            
            # 添加到集合
            self.collection.add(
                embeddings=embeddings,
                documents=batch_texts,
                ids=batch_ids,
                metadatas=batch_metadatas
            )
            
            logger.info(f"已添加 {min(i + batch_size, total)}/{total} 个文档")
        
        logger.info("所有文档添加完成")
    
    def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            top_k: 返回前k个结果
            filter_metadata: 元数据过滤条件
            
        Returns:
            搜索结果列表，每个结果包含 text, metadata, distance
        """
        # 生成查询向量
        query_embedding = self.embedding_model.embed_query(query)
        
        # 执行搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # 格式化结果
        search_results = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i in range(len(results["documents"][0])):
                search_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0
                })
        
        return search_results
    
    def count(self) -> int:
        """
        获取集合中的文档数量
        
        Returns:
            文档数量
        """
        return self.collection.count()
    
    def delete_collection(self):
        """删除集合"""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"已删除集合: {self.collection_name}")
    
    def reset(self):
        """重置集合（删除后重新创建）"""
        try:
            self.delete_collection()
        except:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("集合已重置")

