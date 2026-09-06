"""
使用 LangGraph 的 BaseStore抽象（支持 Redis、Postgres、内存等实现）来存储文件，从而实现跨不同执行线程的持久化存储。
"""

# 案例2-4：配置一个具有持久化记忆的Agent
from deepagents.backends import StoreBackend
from deepagents import create_deep_agent
from langgraph.store.memory import InMemoryStore

from agent.my_llm import llm

agent = create_deep_agent(
    model=llm,
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()  # 使用内存存储，进程重启后丢失。生产环境可用RedisStore等。
)
# Agent写入 /memories/ 下的文件，在后续的新对话中仍可读取。
