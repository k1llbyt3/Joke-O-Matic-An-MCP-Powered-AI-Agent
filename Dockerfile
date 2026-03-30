FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

# Start MCP SSE server on 8081, wait for it, then start FastAPI on $PORT
CMD ["sh", "-c", "python server.py & sleep 3 && uvicorn agent:app --host 0.0.0.0 --port ${PORT:-8080}"]
