import os
import asyncio
import importlib
import importlib.util
import sys

async def main():
    # 1. READ ENVIRONMENT: Which plug are we using?
    framework = os.getenv("FRAMEWORK_TYPE", "langchain")
    user_query = os.getenv("USER_QUERY", "What is the status of my database?")
    
    print(f"--- [SOCKET] Activating {framework} Plug ---")

    try:
        # 2. DYNAMIC IMPORT: This is the "Plug and Play" secret
        # It looks for frameworks/langchain_logic.py
        module_file = os.path.join("frameworks", f"{framework}_logic.py")
        spec = importlib.util.spec_from_file_location(f"{framework}_logic", module_file)
        logic_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = logic_module
        spec.loader.exec_module(logic_module)
        # 3. EXECUTION: Call the standardized 'run_task' function
        # Note: In a full setup, you'd pass your MCP tools here
        result = await logic_module.run_task(user_query) #userquery
        
        print(f"--- [RESULT] ---\n{result}")

    except ImportError:
        print(f"Error: No logic file found for {framework}")
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())