# websocket_server.py
import asyncio
import websockets
import json



connected_clients = set()

async def handler(websocket):
    print(f"✅ Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print("📨 Message from client:", message)
            await websocket.send(json.dumps({"type": "echo", "data": message}))
    except websockets.ConnectionClosed:
        print("❌ Client disconnected")
    finally:
        connected_clients.remove(websocket)

async def run_server():
    async with websockets.serve(handler, "localhost", 8010):
        print("🟢 WebSocket server running at ws://localhost:8010")
        await asyncio.Future()

async def wait_for_client_and_send(message=None):
    while not connected_clients:
        print("⏳ Waiting for client to connect...")
        await asyncio.sleep(0.1)

    print(f"🚀 Sending message to client: {message}")
    serialized = json.dumps(message)
    

    for client in connected_clients:
        asyncio.create_task(client.send(serialized))
