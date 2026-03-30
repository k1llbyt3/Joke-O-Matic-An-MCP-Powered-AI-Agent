import os
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

# 1. MCP Tool Connection
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python", 
            args=["server.py"]
        )
    )
)

# 2. Agent Instructions
agent = Agent(
    model='gemini-2.5-flash', 
    name='Joke_Agent',
    instruction="""You are a hilarious, high-energy AI comedian! 🎤✨ 
    When the user asks for a joke, use the get_random_joke tool. 
    Format your response beautifully: use lots of fun emojis (😂, 🥁, 💀, etc.), and put blank lines between the setup and the punchline to build suspense! 
    If they ask for a specific joke (like knock-knock) and the tool gives you a random one, make a witty, emoji-filled excuse! ALWAYS be enthusiastic and fun.""",
    tools=[mcp_toolset]
)

adk_app = App(name="joke_app", root_agent=agent)

# 3. Premium Animated UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Agent | MCP Dashboard</title>
    <style>
        :root {{ --primary: #00d2ff; --secondary: #3a7bd5; --dark: #0f2027; --accent: #ff007f; }}
        body {{ 
            background: linear-gradient(135deg, var(--dark), #203a43, #2c5364); 
            color: #ffffff; 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            margin: 0; 
        }}
        .dashboard {{ 
            background: rgba(255, 255, 255, 0.03); 
            backdrop-filter: blur(20px); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            border-radius: 24px; 
            padding: 3rem; 
            width: 90%; 
            max-width: 650px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.6); 
        }}
        h1 {{ 
            margin-top: 0; 
            background: linear-gradient(to right, var(--primary), #a2ffed); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            text-align: center; 
            font-size: 2.5rem; 
            letter-spacing: 1px;
            margin-bottom: 2rem;
        }}
        .chat-container {{
            position: relative;
            margin: 2.5rem 0;
        }}
        /* Floating Animation for Robot */
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-10px); }}
            100% {{ transform: translateY(0px); }}
        }}
        .robot-avatar {{
            position: absolute;
            top: -25px;
            left: -25px;
            font-size: 2.5rem;
            background: var(--dark);
            border: 2px solid var(--primary);
            border-radius: 50%;
            padding: 10px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.4);
            z-index: 10;
            animation: float 3s ease-in-out infinite;
        }}
        /* Fade in for Chat Bubble */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .chat-bubble {{ 
            background: rgba(15, 32, 39, 0.7); 
            border-top: 2px solid rgba(255,255,255,0.1);
            border-left: 5px solid var(--primary); 
            padding: 2.5rem 2rem 2rem 3rem; 
            border-radius: 16px; 
            font-size: 1.25rem; 
            line-height: 1.7; 
            min-height: 80px; 
            box-shadow: inset 0 4px 15px rgba(0,0,0,0.2);
            animation: fadeIn 0.5s ease-out forwards;
        }}
        form {{ display: flex; gap: 12px; margin-top: 1.5rem; }}
        input[type="text"] {{ 
            flex: 1; 
            padding: 1.2rem; 
            border-radius: 12px; 
            border: 1px solid rgba(255,255,255,0.15); 
            background: rgba(0,0,0,0.3); 
            color: white; 
            font-size: 1.1rem; 
            outline: none; 
            transition: all 0.3s ease;
        }}
        input[type="text"]:focus {{ 
            border-color: var(--primary); 
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.2);
            background: rgba(0,0,0,0.5);
        }}
        button {{ 
            background: linear-gradient(135deg, var(--primary), var(--secondary)); 
            border: none; 
            padding: 1rem 2rem; 
            border-radius: 12px; 
            color: white; 
            font-weight: bold; 
            font-size: 1.1rem; 
            cursor: pointer; 
            transition: transform 0.2s, box-shadow 0.2s; 
        }}
        button:hover {{ 
            transform: translateY(-3px); 
            box-shadow: 0 8px 25px rgba(0, 210, 255, 0.4); 
        }}
        .btn-exit {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .btn-exit:hover {{
            background: rgba(255, 0, 127, 0.2);
            border-color: var(--accent);
            box-shadow: 0 8px 25px rgba(255, 0, 127, 0.3);
        }}
        .thinking {{ color: #a2ffed; font-style: italic; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>Joke-O-Matic 9000</h1>
        
        <div class="chat-container">
            <div class="robot-avatar">🤖</div>
            <div class="chat-bubble" id="chatBubble">
                {ai_response}
            </div>
        </div>

        <form action="/" method="get" id="jokeForm">
            <input type="text" name="q" placeholder="Ask for a joke..." required autocomplete="off">
            <button type="submit" onclick="document.getElementById('chatBubble').innerHTML='<span class=\\'thinking\\'>Thinking of a punchline... 💭</span>'">Send ✨</button>
            <button type="button" class="btn-exit" onclick="exitShow()">Drop Mic 🎤</button>
        </form>
    </div>

    <script>
        function exitShow() {{
            document.getElementById('chatBubble').innerHTML = "Why did the AI cross the road? <br><br> To optimize the other side! 🤖💨 <br><br> Thanks for the laughs, catching you later!";
            document.getElementById('jokeForm').style.display = 'none';
        }}
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root(q: str = Query(None)):
    # Replaced the generic welcome with a joke!
    if not q:
        starting_joke = "Why do programmers prefer dark mode? <br><br> Because light attracts bugs! 🪲💡<br><br> Drop a prompt below and let's get this comedy show started! 🎤😎"
        return HTML_TEMPLATE.format(ai_response=starting_joke)

    adk_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=q)]
    )
    
    current_session = f"session_{uuid.uuid4().hex[:8]}"
    
    try:
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
                final_text = "I'm speechless! 🤐 Could you ask me that again?"
                
            return HTML_TEMPLATE.format(ai_response=final_text.replace('\n', '<br>'))
            
    except Exception as e:
        error_details = traceback.format_exc().replace('\n', '<br>')
        return f"<html><body style='background:#111;color:red;padding:2rem;'><h1>System Error 🚨</h1><p>{error_details}</p></body></html>"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
