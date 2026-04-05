
import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import importlib.util



#input env - USER_QUESTION, GOOGLE_API_KEY
async def run_task(user_query = "What is the capital of France?"):
    # 1. Grab the question from the Docker environment
    if not user_query:
        print("No user query provided.")
        return
    #user_query = os.getenv("USER_QUESTION", user_query)

    # 2. Grab the API key from the environment
    #openai_api_key = os.getenv("OPENAI_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    # 3. Initialize the model based on provider
    
    # Use Gemini 2.5 Flash model
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_api_key)

    messages = [
        SystemMessage(content="You are a concise AI assistant."),
        HumanMessage(content=user_query)
    ]

    # 4. Get the response
    response = await model.ainvoke(messages)
    print(f"\nAI Response:\n{response.content}")

if __name__ == "__main__":
    asyncio.run(run_task())