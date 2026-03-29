import os
import sys
import uuid
import warnings
import traceback
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams, StdioServerParameters
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

warnings.filterwarnings("ignore")

app = FastAPI()

# Absolute path to server.py — works regardless of working directory on Cloud Run
SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")

# Use sys.executable so we always use the SAME python that's running agent.py
# This guarantees all installed packages (mcp, etc.) are available to server.py
PYTHON_EXECUTABLE = sys.executable

# 3. Interactive UI Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Agent | MCP Dashboard</title>
    <style>
        :root {{ --primary: #00d2ff; --secondary: #3a7bd5; }}
        body {{
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }}
        .dashboard {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 2.5rem;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        }}
        h1 {{
            margin-top: 0;
            background: linear-gradient(to right, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-size: 2.2rem;
        }}
        .chat-bubble {{
            background: rgba(0, 0, 0, 0.3);
            border-left: 4px solid var(--primary);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1.5rem 0;
            font-size: 1.1rem;
            line-height: 1.6;
            min-height: 50px;
        }}
        form {{
            display: flex;
            gap: 10px;
        }}
        input[type="text"] {{
            flex: 1;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.2);
            color: white;
            font-size: 1rem;
            outline: none;
        }}
        input[type="text"]:focus {{
            border-color: var(--primary);
        }}
        button {{
            background: linear-gradient(to right, var(--primary), var(--secondary));
            border: none;
            padding: 1rem 2rem;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
            transition: 0.3s;
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4);
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>Joke-O-Matic AI</h1>
        <div class="chat-bubble">
            {ai_response}
        </div>
        <form action="/" method="get">
            <input type="text" name="q" placeholder="Type your prompt here..." required autocomplete="off">
            <button type="submit">Ask</button>
        </form>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root(q: str = Query(None)):
    if not q:
        return HTML_TEMPLATE.format(
            ai_response="Welcome to the Joke-O-Matic 9000! I was going to tell a joke about a blunt pencil, but there's no point—so give me a prompt and let's see if I can do better!"
        )

    adk_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=q)]
    )

    current_session = f"session_{uuid.uuid4().hex[:8]}"

    try:
        # KEY FIX: Create a fresh McpToolset per request using async context manager.
        # A single global McpToolset shares one stdio subprocess across all requests,
        # but the subprocess exits after the first use, causing "Connection closed"
        # on every subsequent request. Creating it fresh each time gives each request
        # its own clean subprocess lifecycle.
        async with McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=PYTHON_EXECUTABLE,
                    args=[SERVER_PATH]
                )
            )
        ) as mcp_toolset:

            agent = Agent(
                model='gemini-2.5-flash',
                name='Joke_Agent',
                instruction="You are a witty AI comedian. If the user asks for a joke, use your joke tool. Otherwise, just chat with them normally.",
                tools=[mcp_toolset]
            )

            adk_app = App(name="joke_app", root_agent=agent)

            async with InMemoryRunner(app=adk_app) as runner:

                await runner.session_service.create_session(
                    app_name="joke_app",
                    user_id="web_user_99",
                    session_id=current_session
                )

                final_text = ""

                async for event in runner.run_async(
                    new_message=adk_message,
                    user_id="web_user_99",
                    session_id=current_session
                ):
                    if hasattr(event, 'content') and event.content and event.content.parts:
                        final_text = event.content.parts[0].text
                    elif hasattr(event, 'text') and event.text:
                        final_text = event.text

                if not final_text:
                    final_text = "I'm speechless! Could you ask me that again?"

                return HTML_TEMPLATE.format(ai_response=final_text.replace('\n', '<br>'))

    except Exception as e:
        error_details = traceback.format_exc().replace('\n', '<br>')
        return f"<html><body style='background:#111;color:red;padding:2rem;'><h1>System Error</h1><p>{error_details}</p></body></html>"


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
