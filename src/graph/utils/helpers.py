from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from src.graph.state import State
import functools
import asyncio


def convert_messages_to_langchain_format(messages: list[dict[str, str]]):
    langchain_messages : list[BaseMessage] = []
    for message in messages:
        if message["role"] == "user":
            langchain_messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            langchain_messages.append(AIMessage(content=message["content"]))
    return langchain_messages


def error_handler(error_message="Error"):
    def decorator(func):
        async def wrapper(state: State):
            try:
                return await func(state)
            except Exception as e:
                return {"messages": AIMessage(content=f"{error_message}: {e}")}
        return wrapper
    return decorator


def retry_async(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retry_count = 0
            current_delay = delay
            
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    print(f"Retry {retry_count}/{max_retries} after error: {str(e)}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        return wrapper
    return decorator