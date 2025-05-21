import sys
import os
import requests
import argparse
import json
from claude_mcp_client import ClaudeClient

def check_mcp_server():
    mcp_url = os.environ.get("MCP_SERVER_URL", "http://localhost:5001")
    try:
        response = requests.get(f"{mcp_url}/health", timeout=2)
        if response.status_code == 200:
            print("MCP server is running.")
            return True
        else:
            print("MCP server is not running.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to MCP server: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Ask Claude questions with web search capabilities.")
    parser.add_argument("question", nargs="*", help="The question to ask Claude.")
    args = parser.parse_args()

    if args.question:
        query = " ".join(args.question)
    else:
        query = input("Ask Claude: ")

    if not os.environ.get("CLAUDE_API_KEY"):
        print("Please set the CLAUDE_API_KEY environment variable.")
        sys.exit(1)

    if not check_mcp_server():
        sys.exit(1)

    client = ClaudeClient()
    print(f"Searching for '{query}'")

    try:
        answer = client.get_final_answer(query)
        print("Claude's answer:", answer)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()