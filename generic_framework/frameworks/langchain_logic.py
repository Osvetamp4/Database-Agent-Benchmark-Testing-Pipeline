
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
        self.redis_hostname = os.getenv("REDIS_HOSTNAME","redis_storage")
        self.mcp_tools = []

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
            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                google_api_key=self.google_api_key
            )
            self.model = model.bind_tools(self.mcp_tools)
        except Exception as e:
            print(f"Error connecting to the model {e}")

        
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(host=self.redis_hostname, port=6379, db=0, decode_responses=True)
            self.redis_client.set("system_status", "ready")
            print(f"Connected to Redis at {self.redis_hostname}!")
            print("r",self.redis_client)
        except Exception as e:
            print(f"Error connecting to Redis: {e}")


    async def run_task(self,user_query:str):

        print("user_query:", user_query)
        messages = [
                SystemMessage(content="You are a concise AI assistant."),
                HumanMessage(content=user_query)
        ]
        
        # 4. Get the response
        response = await self.model.ainvoke(messages) #Change this so that it also uses tool calls in addition to aiinvoke
        print(f"\nAI Response:\n{response.content}")
        try:
            task_packet = {
                "user_query": user_query,
                "test": "testing"
            }
            # LPUSH adds the item to the list named 'benchmark_tasks'
            # It returns the new length of the list
            queue_length = self.redis_client.lpush("test_tasks", json.dumps(task_packet))
        except Exception as e:
            print(f"Error pushing to Redis: {e}")
    

if __name__ == "__main__":
    pass
    #run_task()