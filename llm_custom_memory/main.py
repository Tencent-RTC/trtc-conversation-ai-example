import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


app = FastAPI(debug=True)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7


class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[dict]
    usage: dict


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        # 将请求消息转换为 LangChain 消息格式
        langchain_messages = []
        for msg in request.messages:
            if msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))


        # add more historys 

        # 使用 LangChain 的 ChatOpenAI 模型
        chat = ChatOpenAI(temperature=request.temperature,
                          model_name=request.model)
        response = chat(langchain_messages)
        print(response)

        # 构造符合 OpenAI API 格式的响应
        return ChatResponse(
            id="chatcmpl-" + "".join([str(ord(c))
                                     for c in response.content[:8]]),
            object="chat.completion",
            created=int(time.time()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response.content
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": -1,  # LangChain 不提供这些信息,所以我们使用占位值
                "completion_tokens": -1,
                "total_tokens": -1
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
