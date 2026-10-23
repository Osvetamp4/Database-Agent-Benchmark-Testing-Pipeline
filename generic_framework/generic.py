import os
import asyncio
import importlib
import importlib.util
import sys
from base_framework import FrameworkLogic
#python loads the program entry point(this file) as __main__
#classes in this program entry point are named __main__.class_name not generic.class_name
#__main__.class is not generic.class



#ADD A LOCK ONTO THIS SO THAT IT ONLY RUNS AND COMMUNICATES TO THE API AFTER BEING GIVEN A SIGNAL
async def main(): #INPUT ENV: FRAMEWORK_TYPE, USER_QUERY, GOOGLE_API_KEY
    framework = os.getenv("FRAMEWORK_TYPE", "langchain")
    user_query = os.getenv("USER_QUERY", "What is the status of my database?")
    
    print(f"--- [SOCKET] Activating {framework} Plug ---")

    try:
        #dynamic import

        module_file = os.path.join("frameworks",f"{framework}_logic.py")#change to no framework folder
        spec = importlib.util.spec_from_file_location(f"{framework}_logic", module_file)
        logic_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = logic_module
        spec.loader.exec_module(logic_module)
        #offload MCP server connection to the framework code instead
        framework_class_name = f"{framework.capitalize()}Logic"
        logic_class = getattr(logic_module,framework_class_name)
        logic = logic_class()
        result = await logic.run_task(user_query) #userquery

        
        
        print(f"--- [RESULT] ---\n{result}")

    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())