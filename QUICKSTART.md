# 快速启动指南

## 前置条件

1. Python 3.8+
2. Java服务已启动（tianji项目）
3. OpenAI API密钥（或其他兼容的LLM服务）

## 安装步骤

### 1. 安装依赖

```bash
cd E:\tj-ai-assistant
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（复制 `.env.example`）：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键项：

```env
# Java服务地址（根据实际情况修改）
JAVA_SERVICE_BASE_URL=http://localhost:8080
JAVA_SERVICE_API_PREFIX=/api

# OpenAI配置（必需）
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo-preview

# 向量数据库路径（可选，使用默认值即可）
CHROMA_DB_PATH=./data/chroma_db

# 嵌入模型（可选，使用默认值即可）
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### 3. 启动服务

```bash
python run.py
```

或者：

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## 首次启动

首次启动时，服务会自动：

1. 检查RAG知识库是否为空
2. 如果为空，自动从Java端同步课程数据
3. 初始化AI Agent

**注意**：确保Java服务已启动，否则数据同步会失败。

## 测试接口

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

### 2. 聊天接口

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "query": "我学Java多线程很吃力，接下来咋办？"
  }'
```

### 3. 手动同步数据

```bash
curl -X POST http://localhost:8000/sync \
  -H "Content-Type: application/json" \
  -d '{
    "force": false
  }'
```

### 4. 查看统计

```bash
curl http://localhost:8000/stats
```

## 使用Python测试客户端

```bash
python test_client.py
```

## 常见问题

### 1. 数据同步失败

**问题**：启动时提示"数据同步失败"

**解决**：
- 检查Java服务是否正常运行
- 检查 `JAVA_SERVICE_BASE_URL` 配置是否正确
- 查看日志了解具体错误信息

### 2. Agent初始化失败

**问题**：提示"AI Agent初始化失败"

**解决**：
- 检查 `OPENAI_API_KEY` 是否正确
- 检查网络连接（能否访问OpenAI API）
- 如果使用其他LLM服务，检查 `OPENAI_BASE_URL` 配置

### 3. 嵌入模型下载慢

**问题**：首次运行时嵌入模型下载很慢

**解决**：
- 这是正常现象，模型会自动下载到本地
- 可以使用国内镜像加速（配置环境变量）

## 下一步

- 查看 `README.md` 了解详细文档
- 根据实际Java接口调整 `services/java_client.py` 中的接口路径
- 自定义系统提示词（修改 `agent/graph.py` 中的 `_build_system_prompt` 方法）

