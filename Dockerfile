FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start MCP SSE server in background, wait for it, then start FastAPI
CMD ["sh", "-c", "python server.py & sleep 3 && uvicorn agent:app --host 0.0.0.0 --port ${PORT:-8080}"]
