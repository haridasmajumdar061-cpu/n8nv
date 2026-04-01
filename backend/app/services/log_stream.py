from collections import defaultdict

from fastapi import WebSocket


class LogStreamManager:
    def __init__(self) -> None:
        self.connections: dict[int, dict[str, WebSocket]] = defaultdict(dict)

    async def connect(self, execution_id: int, connection_id: str, socket: WebSocket) -> None:
        self.connections[execution_id][connection_id] = socket

    async def disconnect(self, execution_id: int, connection_id: str) -> None:
        if execution_id in self.connections and connection_id in self.connections[execution_id]:
            del self.connections[execution_id][connection_id]

    async def broadcast(self, execution_id: int, payload: dict) -> None:
        sockets = self.connections.get(execution_id, {})
        for socket in list(sockets.values()):
            await socket.send_json(payload)


log_stream_manager = LogStreamManager()
