# 项目结构说明

## 目录结构

```
tj-ai-assistant/
├── main.py                    # FastAPI主服务入口
├── run.py                     # 启动脚本
├── config.py                  # 配置管理模块
├── requirements.txt           # Python依赖列表
├── .env.example              # 环境变量示例
├── .gitignore                # Git忽略文件
├── README.md                 # 项目文档
├── QUICKSTART.md             # 快速启动指南
├── PROJECT_STRUCTURE.md      # 本文件
├── test_client.py            # API测试客户端
│
├── agent/                    # Agent模块
│   ├── __init__.py
│   ├── graph.py             # LangGraph编排逻辑
│   └── tools.py             # MCP工具封装
│
├── rag/                      # RAG模块
│   ├── __init__.py
│   ├── embedding.py         # 嵌入模型封装
│   └── vector_store.py      # 向量数据库封装（ChromaDB）
│
└── services/                 # 服务层
    ├── __init__.py
    ├── java_client.py       # Java服务HTTP客户端
    └── data_sync.py         # 数据同步服务
```

## 核心模块说明

### 1. main.py
- FastAPI应用主入口
- 生命周期管理（启动时自动数据预热）
- HTTP API接口定义
- 全局资源管理

### 2. config.py
- 使用 Pydantic Settings 管理配置
- 支持从环境变量读取配置
- 包含所有可配置项

### 3. agent/graph.py
- LangGraph Agent编排
- 实现智能对话流程
- 工具调用和LLM推理

### 4. agent/tools.py
- MCP工具封装
- 提供4个核心工具：
  - `get_user_learning_profile`: 获取用户学习画像
  - `get_user_purchased_courses`: 获取用户购买课程
  - `get_user_learning_records`: 获取用户学习记录
  - `search_courses`: 搜索课程知识库

### 5. rag/vector_store.py
- ChromaDB向量数据库封装
- 文档添加、搜索、统计等功能
- 自动管理嵌入向量

### 6. rag/embedding.py
- Sentence-Transformers嵌入模型封装
- 支持中文多语言模型
- 文档和查询向量化

### 7. services/java_client.py
- Java Spring Cloud服务HTTP客户端
- 异步请求处理
- 封装所有Java端接口调用

### 8. services/data_sync.py
- 数据同步服务
- 从Java端拉取课程数据
- 构建文档并写入向量数据库
- 支持全量和增量同步

## 数据流

### 用户请求处理流程

```
用户请求 (POST /chat)
  ↓
FastAPI路由处理
  ↓
CourseRecommendationAgent.invoke()
  ↓
LangGraph执行
  ├─→ Agent节点 (LLM推理)
  │     ↓
  │   需要工具调用？
  │     ├─ 是 → Tools节点
  │     │        ├─→ 调用Java接口（用户数据）
  │     │        └─→ RAG检索（课程数据）
  │     │             ↓
  │     └─ 否 → 生成最终回复
  │
  └─→ 返回给用户
```

### 数据同步流程

```
服务启动 (lifespan)
  ↓
检查向量数据库
  ├─→ 为空？
  │     ├─ 是 → 调用DataSyncService
  │     │        ├─→ JavaClient获取所有课程
  │     │        ├─→ 获取每门课程详情
  │     │        ├─→ 构建文档文本
  │     │        └─→ 写入向量数据库
  │     │
  │     └─ 否 → 跳过同步
  │
  └─→ 服务就绪
```

## 关键设计决策

### 1. 为什么使用LangGraph而不是LangChain？
- LangGraph更适合处理有状态、多步循环的复杂逻辑
- 可以更好地控制Agent的执行流程
- 支持条件分支和循环

### 2. 为什么使用ChromaDB？
- 轻量级，易于部署
- 支持持久化存储
- 适合中小规模数据
- 如果数据量很大，可以替换为Milvus

### 3. 为什么用户数据不走RAG？
- 用户数据变化频繁，实时性强
- 向量化成本高
- 通过API实时获取更合适

### 4. 为什么课程数据走RAG？
- 课程信息相对稳定
- 需要语义搜索能力
- 适合向量化存储和检索

## 扩展点

### 1. 添加新工具
在 `agent/tools.py` 中添加新工具方法，然后在 `agent/graph.py` 的 `_create_tools()` 中注册。

### 2. 更换LLM
修改 `config.py` 中的LLM配置，支持任何兼容OpenAI API的服务。

### 3. 更换向量数据库
实现新的 `VectorStore` 类，替换 `rag/vector_store.py`。

### 4. 自定义系统提示
修改 `agent/graph.py` 中的 `_build_system_prompt()` 方法。

## 注意事项

1. **首次启动**：确保Java服务已启动，否则数据同步会失败
2. **API密钥**：必须配置有效的OpenAI API密钥
3. **网络连接**：需要能够访问Java服务和LLM服务
4. **数据量**：大量课程数据同步可能需要较长时间
5. **内存占用**：嵌入模型和向量数据库会占用一定内存

