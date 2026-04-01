from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.log_stream import log_stream_manager

router = APIRouter()


@router.websocket("/stream/{execution_id}")
async def stream_logs(websocket: WebSocket, execution_id: int) -> None:
    await websocket.accept()
    connection_id = f"{id(websocket)}"
    await log_stream_manager.connect(execution_id, connection_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await log_stream_manager.disconnect(execution_id, connection_id)
