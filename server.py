import urllib.request
import json
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
    # SSE transport - runs as HTTP server, works on Cloud Run
    mcp.run(transport="sse", host="0.0.0.0", port=8081)
