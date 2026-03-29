# imports
import requests
from mcp.server.fastmcp import FastMCP

# Creates the MCP server
mcp = FastMCP("JokeServer")


# The @mcp.tool decorator exposes this function to your AI agent
@mcp.tool()
def get_random_joke() -> str:
    # Fetches a random joke from a public API.
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    # checks if the request was successful
    if response.status_code == 200:
        data = response.json()
        return f"🎤 {data['setup']}\n\n🥁 *drumroll*...\n\n💥 {data['punchline']} 😂"
    else:
        return "Could not fetch a joke right now. Please Try again later"


if __name__ == "__main__":
    mcp.run()
