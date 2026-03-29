import os
import warnings
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StdioServerParameters,
)
from google.adk.apps import App
from google.adk.runners import InMemoryRunner

warnings.filterwarnings("ignore")

app = FastAPI()

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python", args=["server.py"]
        )
    )
)

agent = Agent(
    model="gemini-2.5-flash",
    name="Joke_Agent",
    instruction="You are a world-class AI stand-up comedian. When asked for a joke, use the get_random_joke tool to fetch the material, but deliver it with maximum comedic flair!",
    tools=[mcp_toolset],
)

adk_app = App(name="joke_app", root_agent=agent)


@app.get("/", response_class=HTMLResponse)
async def root():
    # This runs the agent and formats the output for a web browser!
    async with InMemoryRunner(app=adk_app) as runner:
        response = await runner.run(new_message="Tell me a joke!")
        html_joke = response.text.replace("\n", "<br>")
        return f"<h1>🤖 The Joke-O-Matic 9000</h1><p>{html_joke}</p>"


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
