import os
import re
import json
import requests
from typing import Dict, Any, List,Optional,Literal
from dataclasses import dataclass, asdict
import openai
import anthropic

DUCKDUCKGO_ENDPOINT = "https://api.duckduckgo.com/"
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY","")

LLMProvider = Literal["claude"]

@dataclass
class DDGRequest:
    q: str
    format: str = "json"
    no_html: int = 1
    skip_disambig: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class WebResult:
    title: str
    url: str
    description: str

class MCPClient:
    def __init__(self,endpoint:str = DUCKDUCKGO_ENDPOINT):
        self.endpoint = endpoint
       
    def search(self,query: str, count: int = 10) -> List[WebResult]:
        request = DDGRequest(q=query)

        try:
            response = requests.get(self.endpoint, params=request.to_dict())
            response.raise_for_status()

            data = response.json()
            results = []
            if data.get("Abstract") :
                results.append(WebResult(
                    title = data.get("Heading",""),
                    url = data.get("AbstractURL",""),
                    description = data.get("Abstract","")
                ))

            return results
        except Exception as e:
            print(f"Error fetching data from DuckDuckGo: {e}")
            return []

class ClaudeMCPBridge:
    
    def __init__(self, llm_provider: LLMProvider = "claude"):
        self.llm_provider = llm_provider
        self.mcp_client = MCPClient()
        
        if self.llm_provider == "claude":
            self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        
    def extract_website_queries_with_llm(self, user_message:str)-> List[str]:
        if self.llm_provider == "claude":
            return self._extract_with_cluade(user_message)
        else:
            return ["Error"]

    def _extract_with_cluade(self, user_message:str) -> List[str]:
        try:
            response = self.claude_client.messages.create(
                model = "claude-3-sonnet-20240229",
                max_tokens = 1000,
                temperature = 0.1,
                system = "You are a helpful assistant that extracts website queries from user messages.Extract the website queries from the user message and return them in a JSON format with a 'queries' field with containing an array of Strings. If no queries are found return an empty array.",
                messages = [{"role": "user", "content": user_message}]
            )

            content = response.content[0].text
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)

            if json_match:
                result = json.loads(json_match.group(1))
                
            else:
                try:
                    result = json.loads(content)
                except Error as e:
                    print(f"Error parsing JSON: {e}")
                    return ["error"]   
            return result.get("queries", [])
            
        except Exception as e:
            print(f"Error extracting queries with Claude: {e}")
            return []


def handle_claude_tool_call(tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
    query = tool_parameters.get("query", "")
    if not query:
        return {"error": "No query provided."}

    bridge = ClaudeMCPBridge()
    results = bridge.mcp_client.search(query)

    return {
        "results": [asdict(result) for result in results]
    }    