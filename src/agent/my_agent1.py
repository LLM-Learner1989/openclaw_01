from deepagents import create_deep_agent

from agent.my_llm import llm
from agent.my_tools import web_search

#from langgraph_runtime_inmem.checkpoint import InMemorySaver

#checkpointer = InMemorySaver() # 没加 checkpointer 就不叫会话

from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

agent = create_deep_agent(  # create_agent
    model=llm,
    checkpointer=checkpointer,
    tools=[web_search],
    system_prompt='你是一个助手，请根据用户输入的指令，进行相应的操作。'
)
