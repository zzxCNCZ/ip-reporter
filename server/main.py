import logging
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IP Reporter")

# Mount static files
app.mount("/static", StaticFiles(directory="server/static"), name="static")

# Connection Manager to track active clients
class ConnectionManager:
    def __init__(self):
        # Store active connections: {client_id: {"socket": WebSocket, "ip": str, "connected_at": str}}
        self.active_connections: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str, ip_address: str):
        await websocket.accept()
        self.active_connections[client_id] = {
            "socket": websocket,
            "ip": ip_address,
            "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.info(f"Client connected: {client_id} from {ip_address}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client disconnected: {client_id}")

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection["socket"].send_text(message)
            except Exception:
                pass

    def get_active_clients_info(self):
        return [
            {
                "id": client_id,
                "ip": info["ip"],
                "connected_at": info["connected_at"]
            }
            for client_id, info in self.active_connections.items()
        ]

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    # Serve the static HTML file
    with open("server/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("server/static/favicon.ico")

@app.get("/api/clients")
async def get_clients():
    return manager.get_active_clients_info()

@app.websocket("/ws/client/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    # In a real scenario, we might get the IP from the websocket headers or request
    # Here, we'll try to get it from the client object directly
    client_ip = websocket.client.host if websocket.client else "Unknown"
    
    await manager.connect(websocket, client_id, client_ip)
    try:
        while True:
            # Keep connection alive and listen for any heartbeat if needed
            data = await websocket.receive_text()
            # We could process client heartbeats here
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Error in websocket connection: {e}")
        manager.disconnect(client_id)
