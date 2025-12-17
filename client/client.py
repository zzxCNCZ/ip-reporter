import asyncio
import websockets
import platform
import socket
import logging
import time
import uuid
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SERVER_URL = os.getenv("SERVER_URL", "ws://localhost:8000/ws/client")
CLIENT_ID = f"client-{platform.node()}-{uuid.uuid4().hex[:6]}"

async def monitor_connection():
    uri = f"{SERVER_URL}/{CLIENT_ID}"
    logger.info(f"Connecting to server at {SERVER_URL} with ID {CLIENT_ID}...")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Connected to server successfully!")
                
                # Send initial ping or handshake if needed
                # Here we just keep the connection alive
                try:
                    while True:
                        # Send a heartbeat every 10 seconds
                        await websocket.send("ping")
                        response = await websocket.recv()
                        # logger.debug(f"Received: {response}") # Optional verbose log
                        await asyncio.sleep(10)
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("Connection closed by server")
        except socket.gaierror:
             logger.error("Could not resolve server address. Retrying in 5 seconds...")
        except ConnectionRefusedError:
            logger.error("Connection refused. Is the server running? Retrying in 5 seconds...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Retrying in 5 seconds...")
        
        # Wait before reconnecting
        await asyncio.sleep(5)

def main():
    try:
        asyncio.run(monitor_connection())
    except KeyboardInterrupt:
        logger.info("Client stopping...")

if __name__ == "__main__":
    main()
