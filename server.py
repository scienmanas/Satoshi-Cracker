from fastapi import FastAPI
from main import start_script
import uvicorn
import os
from contextlib import asynccontextmanager
import threading


# Define lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI): 
    # Start the script
    bot_thread = threading.Thread(target=start_script)
    bot_thread.start()

    # Yield control back to FastAPI
    yield

# Make a server
app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root(): 
    return {"message": "Server is running, Satoshi Cracker :)"}

if __name__ == "__main__" :
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info")