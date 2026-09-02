import asyncio
from typing import AsyncIterator

from agent.my_agent2 import agent


async def stream_agent_interaction_corrected(agent, thread_id: str) -> AsyncIterator[str]:
    """
    使用官方推荐的 `agent.stream()` 方法进行流式交互。
    根据调试信息，chunk的结构是 (AIMessageChunk, metadata_dict)
    """
    config = {"configurable": {"thread_id": thread_id}}

    while True: # 多轮对话
        try:
            user_input = input("\n\n[用户] >>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n对话结束。")
            break

        if user_input.lower() in ('quit', 'exit', '退出', 'q'):
            print("再见！")
            break
        if not user_input:
            continue

        print("\n[Agent] >>>> ", end="", flush=True)

        # 准备输入
        inputs = {"messages": [{"role": "user", "content": user_input}]}

        # 关键修正：使用 agent.stream() 并设置 stream_mode
        stream = agent.stream(inputs, config=config, stream_mode="messages", subgraphs=False)

        full_response = ""
        try:
            # 使用同步 for 循环，因为 agent.stream() 返回的是同步生成器
            for chunk in stream:  # 移除 async
                # 根据调试信息，chunk 的结构是 (AIMessageChunk, metadata_dict)
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    token, metadata = chunk

                    # 1. 流式输出 AI 生成的文本内容
                    if hasattr(token, 'content') and token.content is not None:
                        content_str = str(token.content)
                        if content_str:
                            yield content_str  # 生成器
                            full_response += content_str

                    # 2. 捕获并显示工具调用开始
                    if hasattr(token, 'tool_call_chunks') and token.tool_call_chunks:
                        for tool_chunk in token.tool_call_chunks:
                            if tool_chunk and hasattr(tool_chunk, 'get'):
                                if tool_chunk.get('name'):
                                    tool_name = tool_chunk['name']
                                    yield f"\n[调用工具: {tool_name}]\n"

                    # 3. 捕获并显示工具调用结果
                    # 注意：工具调用结果通常不会出现在同一个 token 中
                    # 它们通常以独立的 token 形式出现

                else:
                    # 如果 chunk 不是预期的元组结构，打印调试信息
                    print(f"\n[调试] 意外的 chunk 结构: {type(chunk)}")
                    continue

        except Exception as e:
            yield f"\n❌ Agent 执行出错: {e}\n"
            import traceback
            traceback.print_exc()
            continue


async def main_test():
    # 测试运行Agent，并且进行交互
    thread_id = "demo_thread_01"
    async for response in stream_agent_interaction_corrected(agent, thread_id):
        print(response, end="", flush=True) # 流式输出，设置为 true 表示来一段就打印一段


if __name__ == '__main__':
    asyncio.run(main_test())
