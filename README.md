# Tianji AI Assistant

基于 MCP + LLM + RAG 的个性化课程推荐助手

## 项目简介

这是一个智能课程推荐系统，能够根据用户在商城的学习行为（购买记录、学习时长、学习习惯等），结合课程知识库，提供个性化的课程推荐和学习建议。

## 技术架构

### 核心组件

- **FastAPI**: Web框架，提供HTTP接口
- **LangGraph**: Agent编排框架，实现智能对话流程
- **LangChain**: LLM接口封装
- **ChromaDB**: 向量数据库，存储课程知识库
- **Sentence-Transformers**: 文本嵌入模型
- **MCP**: 模型上下文协议，封装工具调用

### 架构设计

```
用户请求
  ↓
FastAPI (HTTP接口)
  ↓
LangGraph Agent (智能编排)
  ↓
┌─────────────┬──────────────┐
│  MCP Tools   │   RAG检索    │
│ (调用Java)   │  (向量搜索)  │
└─────────────┴──────────────┘
  ↓
LLM (生成回复)
  ↓
返回给用户
```

## 项目结构

```
tj-ai-assistant/
├── main.py                 # FastAPI主服务
├── config.py               # 配置管理
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量示例
├── README.md              # 项目文档（本文件）
├── QUICKSTART.md          # 快速启动指南
├── PROJECT_STRUCTURE.md    # 项目结构说明
├── LLM_CONFIG.md          # LLM配置详细说明
├── API_MAPPING.md         # Java接口映射说明
├── UPDATE_NOTES.md        # 更新说明
├── test_client.py         # API测试客户端
│
├── agent/                 # Agent模块
│   ├── __init__.py       # 模块导出
│   ├── graph.py         # LangGraph编排
│   └── tools.py         # MCP工具封装
│
├── rag/                   # RAG模块
│   ├── __init__.py       # 模块导出
│   ├── embedding.py     # 嵌入模型
│   └── vector_store.py  # 向量数据库
│
└── services/              # 服务层
    ├── __init__.py       # 模块导出
    ├── java_client.py   # Java服务客户端
    └── data_sync.py     # 数据同步服务
```

## 快速开始

### 1. 安装依赖

```bash
cd E:\tj-ai-assistant
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

**关键配置项**：

1. **LLM配置**（必须）：
```env
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo-preview
```

   > 💡 **LLM选择建议**：
   > - **DeepSeek**（推荐）：性价比高，中文效果好
   >   ```env
   >   OPENAI_BASE_URL=https://api.deepseek.com/v1
   >   LLM_MODEL=deepseek-chat
   >   ```
   > - **OpenAI GPT-4**：性能最好，但成本较高
   > - **本地Ollama**：数据安全，无API费用
   > 
   > 详细配置请查看 [LLM_CONFIG.md](LLM_CONFIG.md)

2. **Java服务配置**：
```env
JAVA_SERVICE_BASE_URL=http://localhost:8080
JAVA_SERVICE_API_PREFIX=/api
```

### 3. 启动服务

```bash
python run.py
```

服务将在 `http://localhost:8000` 启动。

### 4. 自动数据预热

服务启动时会自动检查RAG知识库：
- 如果知识库为空，会自动从Java端同步课程数据
- 如果已有数据，则跳过同步

## API接口

### 1. 健康检查

```bash
GET /health
```

### 2. 聊天接口

```bash
POST /chat
Content-Type: application/json

{
  "user_id": 123,
  "query": "我学Java多线程很吃力，接下来咋办？",
  "context": {}
}
```

响应：
```json
{
  "answer": "根据您的学习情况，我建议...",
  "user_id": 123
}
```

### 3. 手动数据同步

```bash
POST /sync
Content-Type: application/json

{
  "force": false
}
```

### 4. 统计信息

```bash
GET /stats
```

## 工作流程

### 用户请求处理流程

1. **用户发起请求**
   - 前端携带 `userId` 和自然语言问题

2. **Agent规划**
   - LLM分析需要获取的信息类型

3. **获取用户画像** (动态数据 - Tool Call)
   - 调用 `get_user_learning_profile` 获取用户学习画像
   - 调用 `get_user_purchased_courses` 获取购买课程
   - 调用 `get_user_learning_records` 获取学习记录

4. **检索课程方案** (静态数据 - RAG)
   - 根据用户痛点，在向量数据库中搜索相关课程

5. **生成建议** (LLM Synthesis)
   - 结合用户画像和课程资料，生成个性化建议

## RAG知识库

### 存储内容

- 课程基本信息（名称、简介）
- 课程详情（介绍、适用人群）
- 课程大纲（章节结构）
- 课程分类信息

### 更新策略

- **自动预热**: 服务启动时，如果知识库为空，自动同步
- **手动同步**: 通过 `/sync` 接口手动触发
- **更新频率**: 仅在课程上架或修改时更新（T+1或手动触发）

## MCP工具

### 可用工具

1. **get_user_learning_profile**: 获取用户学习画像
2. **get_user_purchased_courses**: 获取用户购买的课程
3. **get_user_learning_records**: 获取用户学习记录
4. **search_courses**: 在课程知识库中搜索相关课程

## 开发说明

### Java接口对接

需要确保Java端提供以下接口：

1. **用户学习画像**: `GET /api/lessons/page` (通过课表接口)
2. **用户购买课程**: `GET /api/lessons/page` (课表即代表已购买)
3. **用户学习记录**: `GET /api/learning-records/course/{courseId}`
4. **课程导出**: `GET /api/courses/page` (分页获取，status=2)

详细接口映射请查看 [API_MAPPING.md](API_MAPPING.md)

### 自定义配置

修改 `config.py` 或 `.env` 文件来调整配置。

### 模块导入

项目使用 `__init__.py` 提供清晰的模块导出：

```python
# 导入Agent
from agent import CourseRecommendationAgent, MCPTools

# 导入RAG
from rag import VectorStore, EmbeddingModel

# 导入服务
from services import JavaServiceClient, DataSyncService

# 导入配置
from config import settings
```

## 注意事项

1. **首次启动**: 确保Java服务已启动，否则数据同步会失败
2. **API密钥**: 必须配置有效的LLM API密钥（支持多种服务）
3. **网络连接**: 需要能够访问Java服务和LLM服务
4. **数据量**: 大量课程数据同步可能需要较长时间
5. **内存占用**: 嵌入模型和向量数据库会占用一定内存

## 文档索引

- [快速启动指南](QUICKSTART.md) - 快速上手指南
- [项目结构说明](PROJECT_STRUCTURE.md) - 详细的项目结构
- [LLM配置说明](LLM_CONFIG.md) - LLM服务选择和配置
- [Java接口映射](API_MAPPING.md) - Java接口调用说明
- [更新说明](UPDATE_NOTES.md) - 代码更新记录

## License

MIT
