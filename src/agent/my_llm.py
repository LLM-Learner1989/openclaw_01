"""
创建各类 LLM 模型
"""

from langchain_openai import ChatOpenAI
from agent.env_utils import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    temperature=1.1,
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base=DEEPSEEK_API_BASE,
)


