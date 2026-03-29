import os
import warnings
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams, StdioServerParameters
from google.adk.apps import App
from google.adk.runners import InMemoryRunner

warnings.filterwarnings("ignore")

app = FastAPI()

# Connects to your server.py MCP tool
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python", 
            args=["server.py"]
        )
    )
)

agent = Agent(
    model='gemini-2.5-flash', 
    name='Joke_Agent',
    instruction="You are a world-class AI stand-up comedian. Use the get_random_joke tool and deliver it with flair!",
    tools=[mcp_toolset]
)

adk_app = App(name="joke_app", root_agent=agent)

# UI Template with FIXED double-braces for CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Joke-O-Matic 9000</title>
    <style>
        :root {{ --primary: #8b5cf6; --secondary: #ec4899; }}
        body {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #f8fafc;
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .glass-card {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 3rem;
            width: 90%;
            max-width: 500px;
            text-align: center;
        }}
        h1 {{
            background: linear-gradient(to right, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
        }}
        .joke-container {{
            background: rgba(15, 23, 42, 0.5);
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            border-left: 4px solid var(--primary);
            text-align: left;
        }}
        .btn {{
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            padding: 0.8rem 1.8rem;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="glass-card">
        <h1>Joke-O-Matic</h1>
        <div class="joke-container">
            <p>{joke_content}</p>
        </div>
        <a href="/" class="btn">New Joke ✨</a>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        async with InMemoryRunner(app=adk_app) as runner:
            # FIXED: Passing mandatory keyword arguments per your error logs
            response = await runner.run(
                new_message="Tell me a joke!",
                user_id="user_123",
                session_id="session_456"
            )
            return HTML_TEMPLATE.format(joke_content=response.text.replace('\n', '<br>'))
    except Exception as e:
        return f"<html><body><h1>Agent Error</h1><p>{str(e)}</p></body></html>"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
