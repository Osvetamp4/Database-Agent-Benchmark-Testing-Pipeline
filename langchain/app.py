import os
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

#env - USER_QUESTION
async def ask_question():
    # 1. Grab the question from the Docker environment
    user_query = os.getenv("USER_QUESTION", "What is the capital of France?")
    
    # 2. Initialize the model (v1.0 uses .invoke() by default)
    model = ChatOpenAI(model="gpt-4o")
    
    messages = [
        SystemMessage(content="You are a concise AI assistant."),
        HumanMessage(content=user_query)
    ]
    
    # 3. Get the response
    response = await model.ainvoke(messages)
    print(f"\nAI Response:\n{response.content}")

if __name__ == "__main__":
    asyncio.run(ask_question())