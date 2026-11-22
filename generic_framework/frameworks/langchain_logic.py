
import os
import asyncio

from flask import json
from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import importlib.util
import redis
from base_framework import FrameworkLogic
class LangchainLogic(FrameworkLogic):

    
    async def initialize(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.mcp_url = os.environ["MCP_URL"]
        self.redis_hostname = os.getenv("REDIS_HOST","redis")

        try:
            self.mcp_client = MultiServerMCPClient({
                "local":{
                "transport": "streamable_http",
                "url": self.mcp_url,
                }
            })
            self.mcp_tools = await self.mcp_client.get_tools()
        except Exception as e:
            print(f"Error connecting to the MCP server {e}")

        try:
            model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)
            self.model = model.bind_tools(self.mcp_tools)
        except Exception as e:
            print(f"Error connecting to the model {e}")

        
        self.redis_host = None
        try:
            REDIS_HOST = self.redis_hostname
            self.redis_host = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
            self.redis_host.set("system_status", "ready")
            print(f"Connected to Redis at {REDIS_HOST}!")
            print("r",self.redis_host)
        except Exception as e:
            print(f"Error connecting to Redis: {e}")


    async def run_task(self,user_query:str):

        print("user_query:", user_query)
        messages = [
                SystemMessage(content="You are a concise AI assistant."),
                HumanMessage(content=user_query)
        ]
        
        # 4. Get the response
        response = await self.model.ainvoke(messages)
        print(f"\nAI Response:\n{response.content}")
        try:
            task_packet = {
                "user_query": user_query,
                "test": "testing"
            }
            # LPUSH adds the item to the list named 'benchmark_tasks'
            # It returns the new length of the list
            queue_length = self.redis_host.lpush("test_tasks", json.dumps(task_packet))
        except Exception as e:
            print(f"Error pushing to Redis: {e}")
    

if __name__ == "__main__":
    pass
    #run_task()