
import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage



#env - USER_QUESTION
async def ask_question():
    # 1. Grab the question from the Docker environment
    user_query = os.getenv("USER_QUESTION", "What is the capital of France?")

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
    asyncio.run(ask_question())