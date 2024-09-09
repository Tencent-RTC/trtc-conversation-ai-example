from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks.base import BaseCallbackHandler
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uvicorn
import json
import time

import dotenv

dotenv.load_dotenv()

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置您的OpenAI API密钥
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL") or 'gpt-4o'
BASE_URL = os.getenv("BASE_URL") or 'https://api.openai.com/v1'


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o"
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[dict]
    usage: dict


@tool
def current_time(timezone: str = "UTC") -> str:
    """
    获取当前时间
    """
    return f"The current time in {timezone} is {time.strftime('%H:%M:%S')}."


tools = [current_time]

# 设置代理
MEMORY_KEY = "chat_history"
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        # First put the history
        ("placeholder", "{chat_history}"),
        # Then the new input
        ("human", "{input}"),
        # Finally the scratchpad
        ("placeholder", "{agent_scratchpad}"),
    ]
)

llm = ChatOpenAI(temperature=0, streaming=True, model=MODEL,
                 base_url=BASE_URL, api_key=API_KEY)

agent = create_tool_calling_agent(llm, tools, prompt)

memory = InMemoryChatMessageHistory(session_id="test-session")

agent_executor = AgentExecutor(agent=agent, tools=tools)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)


@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: ChatCompletionRequest):
    messages = request.messages
    human_input = messages[-1].content if messages else ""

    config = {"configurable": {"session_id": "test-session"}}

    response = agent_with_chat_history.invoke({"input": human_input}, config)

    print(response)

    return ChatResponse(
        id="chatcmpl-" + "".join([str(ord(c))
                                  for c in response['output'][:8]]),
        object="chat.completion",
        created=int(time.time()),
        model=request.model,
        choices=[{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response['output']
            },
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": -1,  # LangChain 不提供这些信息,所以我们使用占位值
            "completion_tokens": -1,
            "total_tokens": -1
        }
    )


def format_chunk(chunk, handler, finish=False):
    return {
        "id": handler.response_id,
        "object": "chat.completion.chunk",
        "created": handler.created,
        "model": "gpt-3.5-turbo-0301",
        "choices": [{
            "index": 0,
            "delta": {} if finish else {"content": chunk},
            "finish_reason": "stop" if finish else None
        }]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
