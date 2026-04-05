import docker
import os
import asyncio

# 1. Connect to the local Docker engine
client = docker.from_env()
hashed_containers = dict() # {container_id: container object}
#need to somehow handoff the information of the container id to a redis container.
#framework_handler only handles creation of the containers, send relevant information to a REDIS container

def spawn_worker(framework_name,api_key, user_query):
    print(f"Handler: Spawning unique worker for {framework_name}...")

    # 2. Run the baked image
    container = client.containers.run(
        image="universal-worker:v1",  # Use the exact name you baked
        
        # 3. Inject the "Soul" (Variables)
        environment={
            "FRAMEWORK_TYPE": framework_name,
            "GOOGLE_API_KEY": api_key,
            "USER_QUERY": user_query
        },
        
        # 4. Networking & Cleanup
        detach=True,                    # Run in background
        #auto_remove=True                # Automatically delete when done (no orphans!)
    )
    hashed_containers[container.id] = container
    print(f"Handler: Spawned container {container.id} for {framework_name}")
    #return container.id

async def main(): #Input ENV: FRAMEWORK_LIST, GOOGLE_API_KEY, USER_QUERY
    framework_list = os.getenv("FRAMEWORK_LIST", "null").split(",")
    google_api_key = os.getenv("GOOGLE_API_KEY", "null")
    user_query = os.getenv("USER_QUERY", "What is the status of my database?")
    for i in framework_list:
        spawn_worker(i, google_api_key, user_query)


if __name__ == "__main__":
    asyncio.run(main())