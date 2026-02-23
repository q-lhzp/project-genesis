import sys
import json
import os
from mem0 import Memory

# Configuration for local Mem0 with Qdrant
# We assume Qdrant is running locally (default port 6333)
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "bge-m3",
            "ollama_base_url": "http://localhost:11434",
            "embeddingDims": 1024
        }
    }
}

# Initialize local memory
try:
    m = Memory.from_config(config)
except Exception as e:
    # Fallback/Debug if initialization fails
    m = None
    INIT_ERROR = str(e)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Action required"}))
        sys.exit(1)

    if m is None:
        print(json.dumps({"error": f"Mem0 initialization failed: {INIT_ERROR}"}))
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])
        action = data.get("action")
        user_id = data.get("user_id", "genesis_agent")

        if action == "add":
            text = data.get("text")
            result = m.add(text, user_id=user_id)
            print(json.dumps({"success": True, "result": result}))

        elif action == "search":
            query = data.get("query")
            results = m.search(query, user_id=user_id)
            # Format results for the agent
            memories = [r["memory"] for r in results] if results else []
            print(json.dumps({"success": True, "memories": memories}))

        elif action == "history":
            history = m.history(user_id=user_id)
            print(json.dumps({"success": True, "history": history}))

        else:
            print(json.dumps({"error": f"Unknown action: {action}"}))

    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
