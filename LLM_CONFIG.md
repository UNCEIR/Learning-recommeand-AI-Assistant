# LLM 配置说明

## 为什么选择这些配置？

### 1. LangChain + LangGraph 架构

**选择原因**：
- **LangChain**: 提供统一的LLM接口，支持多种模型（OpenAI、Claude、本地模型等）
- **LangGraph**: 更适合复杂的Agent编排，支持有状态、多步骤的对话流程
- **组合优势**: LangChain处理工具调用，LangGraph处理流程编排

**替代方案**：
- 如果只需要简单对话，可以直接使用 `openai` SDK
- 如果需要更复杂的工具调用，可以考虑 `AutoGen` 或 `CrewAI`

### 2. OpenAI API 作为默认LLM

**当前配置**：
```python
openai_api_key: Optional[str] = None
openai_base_url: str = "https://api.openai.com/v1"
llm_model: str = "gpt-4-turbo-preview"
```

**选择原因**：
- **兼容性好**: OpenAI API格式是行业标准，很多服务都兼容
- **性能优秀**: GPT-4系列模型在理解和推理方面表现优秀
- **易于切换**: 可以轻松切换到其他兼容OpenAI API的服务

**支持的模型**：
- `gpt-4-turbo-preview` / `gpt-4-0125-preview`: 最新GPT-4，性能最好
- `gpt-4`: 稳定版GPT-4
- `gpt-3.5-turbo`: 成本更低，速度更快
- `gpt-4o`: 最新多模态模型

### 3. 如何切换到其他LLM服务？

#### 方案1: 使用兼容OpenAI API的服务

只需修改 `base_url` 和 `api_key`：

```env
# 使用 DeepSeek
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_API_KEY=sk-your-deepseek-key
LLM_MODEL=deepseek-chat

# 使用 智谱AI
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_API_KEY=your-zhipu-key
LLM_MODEL=glm-4

# 使用 阿里云通义千问
OPENAI_BASE_URL=https://dashscope.aliyun.com/compatible-mode/v1
OPENAI_API_KEY=your-dashscope-key
LLM_MODEL=qwen-turbo

# 使用 本地模型（如 Ollama）
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama  # 可以任意值
LLM_MODEL=llama2
```

#### 方案2: 使用其他LangChain支持的模型

修改 `agent/graph.py` 中的LLM初始化：

```python
# 使用 Anthropic Claude
from langchain_anthropic import ChatAnthropic
self.llm = ChatAnthropic(
    model="claude-3-opus-20240229",
    anthropic_api_key=settings.anthropic_api_key
)

# 使用 Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
self.llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=settings.google_api_key
)

# 使用本地模型（通过Ollama）
from langchain_community.llms import Ollama
self.llm = Ollama(model="llama2")
```

### 4. 嵌入模型配置

**当前配置**：
```python
embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

**选择原因**：
- **多语言支持**: `multilingual` 版本支持中文
- **轻量级**: 模型较小，加载快
- **性能平衡**: 在速度和效果之间取得平衡

**其他推荐模型**：

```python
# 中文优化模型（推荐）
"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # 当前使用
"BAAI/bge-large-zh-v1.5"  # 中文效果更好，但模型更大
"moka-ai/m3e-base"  # 专门针对中文优化

# 英文模型
"sentence-transformers/all-MiniLM-L6-v2"  # 更小更快
"sentence-transformers/all-mpnet-base-v2"  # 效果更好

# 多语言大模型
"sentence-transformers/paraphrase-multilingual-mpnet-base-v2"  # 效果最好但最慢
```

**切换方法**：
修改 `.env` 文件：
```env
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

### 5. 成本优化建议

#### 方案1: 使用更便宜的模型
```env
# 使用 GPT-3.5 而不是 GPT-4
LLM_MODEL=gpt-3.5-turbo
```

#### 方案2: 使用本地模型
```env
# 使用 Ollama 本地部署
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama2:7b
```

#### 方案3: 使用国内服务（通常更便宜）
```env
# DeepSeek（性价比高）
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

### 6. 性能优化建议

#### 1. 调整温度参数
```python
# 在 agent/graph.py 中
self.llm = ChatOpenAI(
    model=settings.llm_model,
    temperature=0.7,  # 降低到0.3-0.5可以获得更确定性的回答
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url
)
```

#### 2. 使用流式响应
```python
# 如果需要流式输出，可以修改 main.py
async def chat_stream(request: ChatRequest):
    async for chunk in agent.invoke_stream(...):
        yield chunk
```

#### 3. 缓存工具调用结果
可以在 `agent/tools.py` 中添加缓存机制，避免重复调用相同接口。

### 7. 配置示例

#### 开发环境（使用本地模型）
```env
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
LLM_MODEL=llama2:7b
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

#### 生产环境（使用GPT-4）
```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-your-production-key
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
```

#### 国内环境（使用DeepSeek）
```env
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_API_KEY=sk-your-deepseek-key
LLM_MODEL=deepseek-chat
EMBEDDING_MODEL=moka-ai/m3e-base
```

### 8. 常见问题

#### Q: 如何测试不同的模型？
A: 修改 `.env` 文件中的 `LLM_MODEL`，重启服务即可。

#### Q: 模型切换后需要重新构建RAG知识库吗？
A: 不需要。RAG知识库与LLM模型是独立的，只有嵌入模型影响知识库。

#### Q: 如何同时支持多个模型？
A: 可以在配置中添加多个模型配置，然后在代码中根据请求选择。

#### Q: 本地模型性能如何？
A: 取决于硬件配置。7B参数的模型在16GB内存的机器上可以运行，但效果可能不如GPT-4。

### 9. 推荐配置

**预算充足**：
- LLM: `gpt-4-turbo-preview`
- Embedding: `BAAI/bge-large-zh-v1.5`

**平衡方案**：
- LLM: `gpt-3.5-turbo` 或 `deepseek-chat`
- Embedding: `moka-ai/m3e-base`

**成本优先**：
- LLM: 本地模型（Ollama + llama2:7b）
- Embedding: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
