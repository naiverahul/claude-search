import os
import json
import time
import requests
from typing import List, Dict, Any, Optional

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")

class ClaudeClient:
    def __init__(self, api_key: str = CLAUDE_API_KEY, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.mcp_url = MCP_SERVER_URL
        self.model = model
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        self.tools = [{
            "name": "web_content",
            "description": "Retrieves information from the website, based on the user's query.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search or website to look up for information."
                    }
                },
                "required": ["query"]
            }
        }]
        
        self.check_mcp_server()

    def check_mcp_server(self) -> bool:
        try:
            response = requests.get(f"{self.mcp_url}/health", timeout=2)
            if response.status_code == 200:
                print("MCP server is running.")
                return True
            else:
                print("MCP server is not running.")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to MCP server: {e}")
            return False

    def send_message(self, message: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:  # Renamed parameter for consistency
        if not self.api_key:
            raise ValueError("API key is not set. Please set the CLAUDE_API_KEY environment variable.")
        
        if conversation_history is None:
            conversation_history = []
        
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": conversation_history + [{"role": "user", "content": message}],
            "tools": self.tools,
        }

        print(f"Sending message to Claude: {message}")

        try:
            response = requests.post(
                CLAUDE_API_URL,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                print(response.json())
                print("Error")

            response.raise_for_status()

            result = response.json()
            print("Claude's response:", result)

            has_tool_call = False
            tool_call: Dict[str, Any] = {}

            if "content" in result:
                for content_block in result.get("content", []):
                    if content_block.get("type") == "tool_use":
                        has_tool_call = True
                        print("Tool call detected.")
                        tool_call["name"] = content_block.get("name", "")
                        tool_call["parameters"] = {}

                        tool_call["parameters"]["query"] = content_block.get("input", {}).get("query", "")
                        print(f"Tool call details: {tool_call}")
                        
                        tool_response = self._handle_tool_call(tool_call)
                        print(f"Tool response: {tool_response}")

                        conversation_history.append({
                            "role": "user",
                            "content": message
                        })

                        conversation_history.append({
                            "role": "assistant",
                            "content": [
                                {"type": "text", "text": (
                                    result.get("content", [{}])[0].get("text", "")
                                    + "\n\nThe tool call was successful and here is the information from the tool call: "
                                    + tool_response["results"][0]["description"]
                                )}
                            ]
                        })

                        return self.send_message(
                            "Please summarize the information from the tool call and dont send any more tool calls",
                            conversation_history
                        )

            if not has_tool_call:
                print("No tool call detected.")

            return result
        except Exception as e:
            print(f"Error sending message: {e}")

    def _handle_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = tool_call.get("name")
        tool_parameters = tool_call.get("parameters")

        if not self.check_mcp_server():
            return {"Error": "MCP server is not running."}

        max_retries = 3
        try_count = 0
        while try_count < max_retries:
            try:
                response = requests.post(
                    f"{MCP_SERVER_URL}/tools/{tool_name}",
                    json={"name": tool_name, "parameters": tool_parameters},
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                retry_count += 1  # incorrect variable
                try_count += 1  # Fixed retry counter name
                if try_count < max_retries:
                    wait_time = 2 ** try_count
                    time.sleep(wait_time)
                else:
                    return {
                        "Error": f"Failed to call tool {tool_name} after {max_retries} attempts: {e}"
                    }

    def get_final_answer(self, query: str) -> str:
        conversation_history: List[Dict[str, Any]] = []  # Explicitly initialize
        try:
            response = self.send_message(query, conversation_history)

            if "content" in response:
                for content_block in response.get("content", []):
                    if content_block.get("type") == "text":
                        return content_block.get("text", "")
            return "No answer found."

        except Exception as e:
            return f"Error getting final answer: {e}"
