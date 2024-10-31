# FastAPI LangChain Function Calling 

## Installation

1. Ensure you have Python 3.7+ installed.

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install fastapi uvicorn langchain-openai langchain pydantic python-dotenv
```

## Configuration

1. Create a `.env` file in the project root directory and add the following:
```
OPENAI_API_KEY=your_openai_api_key_here
MODEL=gpt-4  # or other model you want to use
BASE_URL=https://api.openai.com/v1  # can be omitted if using default OpenAI API
```

2. Replace `your_openai_api_key_here` with your OpenAI API key.

## Running the Application

1. Run in command line:
```bash
python main.py
```

2. The application will start at `http://0.0.0.0:8000`.

## Using the API

The application provides a POST endpoint `/v1/chat/completions` for sending chat requests.

Example request:
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

The API will return a JSON response containing the AI assistant's reply.

## Notes

- This application uses the FastAPI framework and LangChain library.
- It includes a custom tool `current_time` that can get the current time.
- The application uses memory storage for chat history, which will be lost after restart.
- CORS middleware is enabled, allowing requests from all origins.

## Customization

- To add new tools, add new `@tool` decorated functions to the `tools` list.
- You can customize the system prompt by modifying the `prompt` variable.
- Different OpenAI models can be selected by changing the `MODEL` environment variable.

