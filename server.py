import asyncio
import requests
from mcp.server import Server
import mcp.types as types
from mcp.server.stdio import stdio_server

app = Server("joke-server")

@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="get_random_joke",
            description="Fetches a random joke.",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_random_joke":
        try:
            resp = requests.get("https://official-joke-api.appspot.com/random_joke")
            if resp.status_code == 200:
                data = resp.json()
                joke = f"{data['setup']} - {data['punchline']}"
                return [types.TextContent(type="text", text=joke)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    return [types.TextContent(type="text", text="Failed to fetch joke.")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
