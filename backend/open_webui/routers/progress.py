# progress.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from open_webui.utils.auth import get_verified_user
import asyncio
import json
import threading

progress_queue = asyncio.Queue()

def update_progress(current, total):
    progress = round((current / total) * 100, 2)
    msg = {"progress": progress, "completed": current, "total": total}
    message = f"data: {json.dumps(msg)}\n\n"

    def push_to_queue():
        try:
            progress_queue.put_nowait(message)
            print(f" Queued progress: {progress}%")
        except Exception as e:
            print(" Failed to queue message:", e)

    # Use a thread to ensure it always runs outside blocking context
    threading.Thread(target=push_to_queue).start()






router = APIRouter()

@router.get("/process/file/stream")
async def process_file_stream(request: Request):
    async def event_stream():
        while True:
            data = await progress_queue.get()
            print("sending SSE data:", data.strip())
            yield data

    return StreamingResponse(event_stream(), media_type="text/event-stream")



