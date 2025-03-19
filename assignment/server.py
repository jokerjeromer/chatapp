import asyncio
import websockets
import json

# Store connected clients
connected_clients = set()

async def handle_client(websocket, path):
    # Register client
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Broadcast message to all connected clients
            for client in connected_clients:
                try:
                    await client.send(message)
                except websockets.ConnectionClosed:
                    connected_clients.remove(client)
    except websockets.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("Chat server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main()) 