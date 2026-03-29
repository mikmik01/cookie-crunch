import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.models import QueryRequest
from api.pipeline import run_pipeline

router = APIRouter()


def make_event(
    step: str,
    message: str,
    done: bool = False,
    error: str = None,
    data: dict = None,
) -> str:
    payload = {"step": step, "message": message, "done": done}
    if error:
        payload["error"] = error
    if data:
        payload["data"] = data
    return f"data: {json.dumps(payload)}\n\n"


async def stream_pipeline(user_query: str):
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def run():
        try:
            for step, message, result in run_pipeline(user_query):
                loop.call_soon_threadsafe(queue.put_nowait, (step, message, result, None))
        except Exception as e:
            loop.call_soon_threadsafe(queue.put_nowait, ("error", str(e), None, e))
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    loop.run_in_executor(None, run)

    while True:
        item = await queue.get()
        if item is None:
            break

        step, message, result, exc = item

        if exc is not None:
            yield make_event("error", "Pipeline failed.", done=True, error=str(exc))
            break

        if result is not None:
            yield make_event("done", message, done=True, data=result)
        else:
            yield make_event(step, message)


@router.post("/query")
async def query_meta(request: QueryRequest):
    return StreamingResponse(
        stream_pipeline(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )