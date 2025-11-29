"""
RAG模块：向量数据库和嵌入模型

本模块提供RAG（检索增强生成）功能，包括：
- VectorStore: 向量数据库封装（ChromaDB）
- EmbeddingModel: 嵌入模型封装

使用示例：
    from rag import VectorStore, EmbeddingModel
    
    # 初始化向量数据库
    vector_store = VectorStore(collection_name="courses")
    
    # 搜索相似文档
    results = vector_store.search("Java多线程", top_k=5)
    
    # 初始化嵌入模型
    embedding_model = EmbeddingModel()
    
    # 向量化文档
    embeddings = embedding_model.embed_documents(["文档1", "文档2"])
"""

from rag.vector_store import VectorStore
from rag.embedding import EmbeddingModel

__version__ = "1.0.0"
__all__ = [
    "VectorStore",
    "EmbeddingModel",
]

