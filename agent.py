import os
import warnings
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams, StdioServerParameters
from google.adk.apps import App
from google.adk.runners import InMemoryRunner

# Silence unnecessary background noise in the logs
warnings.filterwarnings("ignore")

app = FastAPI()

# 1. Define the MCP Toolset (Connects to your server.py)
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python", 
            args=["server.py"]
        )
    )
)

# 2. Create the Agent with Comedian Instructions
agent = Agent(
    model='gemini-2.5-flash', 
    name='Joke_Agent',
    instruction="You are a world-class AI stand-up comedian. When asked for a joke, use the get_random_joke tool to fetch the material, but deliver it with maximum comedic flair! Add witty commentary and a funny remark at the end.",
    tools=[mcp_toolset]
)

adk_app = App(name="joke_app", root_agent=agent)

# 3. Premium Glassmorphism UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Joke-O-Matic 9000 | Gen AI Academy</title>
    <style>
        :root {{ --primary: #8b5cf6; --secondary: #ec4899; }}
        body {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #f8fafc;
            font-family: 'Inter', sans-serif;
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
            max-width: 550px;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        .badge {{
            background: rgba(139, 92, 246, 0.2);
            color: #a78bfa;
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            display: inline-block;
        }}
        h1 {{
            font-size: 2.5rem;
            margin: 0 0 1.5rem 0;
            background: linear-gradient(to right, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .joke-container {{
            background: rgba(15, 23, 42, 0.5);
            padding: 2rem;
            border-radius: 16px;
            margin: 1.5rem 0;
            border-left: 4px solid var(--primary);
            text-align: left;
        }}
        .joke-text {{ font-size: 1.25rem; line-height: 1.7; color: #e2e8f0; }}
        .btn {{
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            transition: all 0.3s ease;
        }}
        .btn:hover {{ transform: translateY(-2px); filter: brightness(1.1); }}
    </style>
</head>
<body>
    <div class="glass-card">
        <span class="badge">Track 2: MCP & ADK Integration</span>
        <h1>Joke-O-Matic 9000</h1>
        <div class="joke-container">
            <div class="joke-text">{joke_content}</div>
        </div>
        <a href="/" class="btn">Generate New Comedy ✨</a>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        async with InMemoryRunner(app=adk_app) as runner:
            # FIXED: Using explicit keyword arguments for the latest ADK version
            response = await runner.run(
                new_message="Tell me a joke!",
                user_id="web_user_001",
                session_id="session_id_999"
            )
            
            # Clean up newlines for the web browser
            formatted_joke = response.text.replace('\n', '<br>')
            return HTML_TEMPLATE.format(joke_content=formatted_joke)
    except Exception as e:
        # If something goes wrong, this will show you the error instead of a blank 500 page
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == "__main__":
    import uvicorn
    # Cloud Run provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
