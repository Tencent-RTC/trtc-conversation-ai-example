
# FastAPI LangChain Function Calling 

## 安装

1. 确保您已安装 Python 3.7+。

2. 创建并激活虚拟环境（可选但推荐）：
```bash
python -m venv venv
source venv/bin/activate  # 在 Windows 上使用 venv\Scripts\activate
```

3. 安装所需依赖：
```bash
pip install fastapi uvicorn langchain-openai langchain pydantic python-dotenv
```

## 配置

1. 在项目根目录创建 `.env` 文件，并添加以下内容：
```
OPENAI_API_KEY=your_openai_api_key_here
MODEL=gpt-4  # 或其他您想使用的模型
BASE_URL=https://api.openai.com/v1  # 如果使用默认 OpenAI API，可以省略此行
```

2. 将您的 OpenAI API 密钥替换 `your_openai_api_key_here`。

## 运行应用

1. 在命令行中运行：
```bash
python main.py
```

2. 应用将在 `http://0.0.0.0:8000` 上启动。

## 使用 API

应用提供了一个 POST 端点 `/v1/chat/completions`，用于发送聊天请求。

示例请求：
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-4",
       "messages": [
         {"role": "user", "content": "What time is it now?"}
       ]
     }'
```

API 将返回一个包含 AI 助手回复的 JSON 响应。

## 注意事项

- 此应用使用 FastAPI 框架和 LangChain 库。
- 它包含一个自定义工具 `current_time`，可以获取当前时间。
- 应用使用内存存储聊天历史，重启后历史将丢失。
- CORS 中间件已启用，允许所有来源的请求。

## 自定义

- 要添加新工具，在 `tools` 列表中添加新的 `@tool` 装饰函数。
- 可以通过修改 `prompt` 变量来自定义系统提示。
- 通过更改 `MODEL` 环境变量可以选择不同的 OpenAI 模型。

