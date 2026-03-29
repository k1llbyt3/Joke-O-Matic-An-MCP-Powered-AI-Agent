FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# start.sh launches both the MCP SSE server and the FastAPI app
RUN echo '#!/bin/sh\npython server.py &\nsleep 2\nuvicorn agent:app --host 0.0.0.0 --port ${PORT:-8080}' > /workspace/start.sh
RUN chmod +x /workspace/start.sh

ENV PORT=8080
EXPOSE 8080

CMD ["/workspace/start.sh"]
