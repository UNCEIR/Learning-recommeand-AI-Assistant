"""
配置管理模块

提供应用配置管理，支持从环境变量读取配置。

使用示例：
    from config import settings
    
    # 访问配置
    print(settings.java_service_base_url)
    print(settings.llm_model)
    
    # 配置会自动从 .env 文件或环境变量读取
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    应用配置类
    
    所有配置项都可以通过环境变量或 .env 文件设置。
    环境变量名称使用大写，下划线分隔（如：JAVA_SERVICE_BASE_URL）
    """
    
    # ========== Java服务配置 ==========
    java_service_base_url: str = "http://localhost:8080"
    """Java服务的基础URL，如：http://localhost:8080"""
    
    java_service_api_prefix: str = "/api"
    """API路径前缀，如：/api"""
    
    # ========== LLM配置 ==========
    openai_api_key: Optional[str] = None
    """
    OpenAI API密钥（或其他兼容服务的API密钥）
    如果使用其他服务，只需修改 base_url 和 api_key
    支持的服务：OpenAI、DeepSeek、智谱AI、阿里云通义千问、Ollama等
    详见 LLM_CONFIG.md
    """
    
    openai_base_url: str = "https://api.openai.com/v1"
    """
    LLM服务的API地址
    - OpenAI: https://api.openai.com/v1
    - DeepSeek: https://api.deepseek.com/v1
    - 智谱AI: https://open.bigmodel.cn/api/paas/v4
    - 本地Ollama: http://localhost:11434/v1
    """
    
    llm_model: str = "gpt-4-turbo-preview"
    """
    使用的LLM模型名称
    推荐模型：
    - gpt-4-turbo-preview: 最新GPT-4，效果最好
    - gpt-3.5-turbo: 成本更低，速度更快
    - deepseek-chat: 性价比高
    - llama2:7b: 本地模型（需配合Ollama）
    详见 LLM_CONFIG.md
    """
    
    # ========== 向量数据库配置 ==========
    chroma_db_path: str = "./data/chroma_db"
    """ChromaDB向量数据库的存储路径"""
    
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    """
    嵌入模型名称（用于文本向量化）
    推荐模型：
    - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2: 当前使用，多语言支持
    - BAAI/bge-large-zh-v1.5: 中文效果更好
    - moka-ai/m3e-base: 专门针对中文优化
    详见 LLM_CONFIG.md
    """
    
    # ========== 服务配置 ==========
    server_host: str = "0.0.0.0"
    """FastAPI服务监听地址，0.0.0.0表示监听所有网络接口"""
    
    server_port: int = 8000
    """FastAPI服务监听端口"""
    
    # ========== 日志配置 ==========
    log_level: str = "INFO"
    """
    日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
    DEBUG: 最详细，包含所有调试信息
    INFO: 一般信息（推荐）
    WARNING: 只显示警告和错误
    ERROR: 只显示错误
    """
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()

__all__ = ["Settings", "settings"]

