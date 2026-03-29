import urllib.request
import json
import uvicorn
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("JokeServer")

@mcp.tool()
def get_random_joke() -> str:
    """Fetches a random joke from a public API."""
    try:
        with urllib.request.urlopen("https://official-joke-api.appspot.com/random_joke") as response:
            data = json.loads(response.read().decode())
            return f"🎤 {data['setup']}\n\n🥁 *drumroll*...\n\n💥 {data['punchline']} 😂"
    except Exception:
        return "Could not fetch a joke right now. Please try again later."

if __name__ == "__main__":
    # Use uvicorn directly — more stable than mcp.run() in containers
    mcp_app = mcp.get_asgi_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8081)
