FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

# Start MCP server in background, wait 3s for it to be ready, then start FastAPI
CMD ["sh", "-c", "python server.py & sleep 3 && uvicorn agent:app --host 0.0.0.0 --port ${PORT:-8080}"]
