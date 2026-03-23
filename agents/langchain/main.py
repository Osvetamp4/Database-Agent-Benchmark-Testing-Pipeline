# Inside your Docker Worker
#langgraph.checkpoint.postgres
from langgraph.checkpoint.postgres import PostgresSaver
from my_agent_logic import graph

# Interfacing with the graph
config = {"configurable": {"thread_id": "user_123"}}
for event in graph.stream({"messages": [("user", "Get total sales.")]}, config):
    # This is how you "talk" to the framework
    print(event)

import asyncio
from langchain_openai import ChatOpenAI

async def run_langchain_worker():
    model = ChatOpenAI(model="gpt-4o")
    # You interface via 'ainvoke' to keep the event loop non-blocking
    response = await model.ainvoke("Get the last 5 records from PG.")
    print(response.content)

asyncio.run(run_langchain_worker())
