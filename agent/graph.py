"""
LangGraph Agent编排：实现智能对话流程
"""
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from loguru import logger
from config import settings
from agent.tools import MCPTools


class AgentState(TypedDict):
    """Agent状态"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: int
    context: dict


class CourseRecommendationAgent:
    """课程推荐Agent"""
    
    def __init__(self):
        """初始化Agent"""
        # 初始化工具
        self.tools = MCPTools()
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.7,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        
        # 创建LangChain工具
        self.langchain_tools = self._create_tools()
        
        # 绑定工具到LLM
        self.llm_with_tools = self.llm.bind_tools(self.langchain_tools)
        
        # 构建图
        self.graph = self._build_graph()
    
    def _create_tools(self):
        """创建工具列表"""
        from langchain_core.tools import StructuredTool
        from pydantic import BaseModel, Field
        from typing import Optional
        
        # 定义工具函数
        async def get_user_learning_profile(user_id: int):
            """获取用户学习画像"""
            return await self.tools.get_user_learning_profile(user_id)
        
        async def get_user_purchased_courses(user_id: int):
            """获取用户购买的课程"""
            return await self.tools.get_user_purchased_courses(user_id)
        
        async def get_user_learning_records(user_id: int, course_id: Optional[int] = None):
            """获取用户学习记录"""
            return await self.tools.get_user_learning_records(user_id, course_id)
        
        async def search_courses(query: str, top_k: int = 5):
            """在课程知识库中搜索相关课程"""
            return await self.tools.search_courses(query, top_k)
        
        # 创建工具
        tools = [
            StructuredTool.from_function(
                func=get_user_learning_profile,
                name="get_user_learning_profile",
                description="获取用户的学习画像，包括学习时长、学习习惯、学习进度等信息"
            ),
            StructuredTool.from_function(
                func=get_user_purchased_courses,
                name="get_user_purchased_courses",
                description="获取用户购买的所有课程列表"
            ),
            StructuredTool.from_function(
                func=get_user_learning_records,
                name="get_user_learning_records",
                description="获取用户的学习记录，包括学习时长、学习进度、卡点等信息"
            ),
            StructuredTool.from_function(
                func=search_courses,
                name="search_courses",
                description="在课程知识库中搜索相关课程，用于推荐和匹配"
            )
        ]
        
        return tools
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self._tools_node)
        
        # 设置入口点
        workflow.set_entry_point("agent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # 工具执行后返回agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    async def _agent_node(self, state: AgentState) -> AgentState:
        """Agent节点：LLM推理"""
        messages = state["messages"]
        user_id = state.get("user_id", 0)
        context = state.get("context", {})
        
        # 构建系统提示
        system_prompt = self._build_system_prompt(user_id, context)
        system_message = SystemMessage(content=system_prompt)
        
        # 调用LLM
        response = await self.llm_with_tools.ainvoke([system_message] + list(messages))
        
        return {"messages": [response]}
    
    def _build_system_prompt(self, user_id: int, context: dict) -> str:
        """构建系统提示"""
        prompt = """你是一个专业的课程推荐助手，能够根据用户的学习情况提供个性化的课程推荐和学习建议。

你的任务：
1. 分析用户的学习画像（购买课程、学习时长、学习习惯等）
2. 识别用户的学习痛点和需求
3. 从课程知识库中搜索匹配的课程
4. 提供个性化的学习建议和课程推荐

可用工具：
- get_user_learning_profile: 获取用户学习画像
- get_user_purchased_courses: 获取用户购买的课程
- get_user_learning_records: 获取用户学习记录
- search_courses: 在课程知识库中搜索相关课程

请根据用户的问题，智能地调用这些工具，然后基于收集到的信息给出专业的建议。
"""
        return prompt
    
    async def _tools_node(self, state: AgentState) -> AgentState:
        """工具节点：执行工具调用"""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_calls = []
        tool_results = []
        
        # 提取工具调用
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})
                
                logger.info(f"调用工具: {tool_name}, 参数: {tool_args}")
                
                # 执行工具
                try:
                    # 根据工具名称找到对应的工具并执行
                    tool_func = None
                    for tool in self.langchain_tools:
                        if tool.name == tool_name:
                            tool_func = tool
                            break
                    
                    if tool_func:
                        # 调用工具
                        if tool_name == "get_user_learning_profile":
                            result = await self.tools.get_user_learning_profile(
                                tool_args.get("user_id")
                            )
                        elif tool_name == "get_user_purchased_courses":
                            result = await self.tools.get_user_purchased_courses(
                                tool_args.get("user_id")
                            )
                        elif tool_name == "get_user_learning_records":
                            result = await self.tools.get_user_learning_records(
                                tool_args.get("user_id"),
                                tool_args.get("course_id")
                            )
                        elif tool_name == "search_courses":
                            result = await self.tools.search_courses(
                                tool_args.get("query"),
                                tool_args.get("top_k", 5)
                            )
                        else:
                            result = {"error": f"未知工具: {tool_name}"}
                    else:
                        result = {"error": f"未找到工具: {tool_name}"}
                    
                    # 将结果转换为字符串
                    if isinstance(result, (dict, list)):
                        import json
                        result_str = json.dumps(result, ensure_ascii=False, indent=2)
                    else:
                        result_str = str(result)
                    
                    tool_results.append({
                        "tool_call_id": tool_call.get("id", ""),
                        "content": result_str
                    })
                except Exception as e:
                    logger.error(f"工具执行失败: {e}")
                    tool_results.append({
                        "tool_call_id": tool_call.get("id", ""),
                        "content": f"工具执行失败: {str(e)}"
                    })
        
        # 构建工具结果消息
        from langchain_core.messages import ToolMessage
        tool_messages = [
            ToolMessage(
                content=result["content"],
                tool_call_id=result["tool_call_id"]
            )
            for result in tool_results
        ]
        
        return {"messages": tool_messages}
    
    def _should_continue(self, state: AgentState) -> str:
        """判断是否继续"""
        messages = state["messages"]
        last_message = messages[-1]
        
        # 如果有工具调用，继续执行
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        # 否则结束
        return "end"
    
    async def invoke(self, user_id: int, query: str, context: dict = None) -> str:
        """
        执行Agent推理
        
        Args:
            user_id: 用户ID
            query: 用户查询
            context: 上下文信息
            
        Returns:
            Agent回复
        """
        # 构建初始状态
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "user_id": user_id,
            "context": context or {}
        }
        
        # 执行图
        final_state = await self.graph.ainvoke(initial_state)
        
        # 提取最终回复
        messages = final_state["messages"]
        last_message = messages[-1]
        
        if isinstance(last_message, AIMessage):
            return last_message.content
        else:
            return str(last_message.content)
    
    async def close(self):
        """关闭Agent"""
        await self.tools.close()

