# webrtc_server.py
import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.contrib.signaling import BYE
from aiortc.contrib.media import MediaBlackhole
from aiortc import RTCDataChannel
import websockets
import threading

peer_connection = None
data_channel = None
data_channel_ready = asyncio.Event() 

virtual_time_callback = None

def register_virtual_time_callback(callback):
    global virtual_time_callback
    virtual_time_callback = callback


async def signaling_handler(websocket):
    global peer_connection, data_channel

    print("📡 WebRTC signaling connected")

    pc = RTCPeerConnection()
    peer_connection = pc

    @pc.on("datachannel")
    def on_datachannel(channel: RTCDataChannel):
        global data_channel
        data_channel = channel
        print(f"🛰️ Data channel created: {channel.label}")
        
        data_channel_ready.set()

        @channel.on("message")
        def on_message(message):
            # print(f"📥 Message received from browser: {message}")
            # You can respond back via data_channel.send()
            msg = json.loads(message)
            if msg["type"] == "set_time":
                sim_seconds = int(msg["value"])
                if virtual_time_callback:
                    threading.Thread(target=virtual_time_callback, args=(sim_seconds,)).start()
                else:
                    print("⚠️ Callback for set_time not set")

    async for message in websocket:
        msg = json.loads(message)
        if msg["type"] == "offer":
            offer = RTCSessionDescription(sdp=msg["sdp"], type=msg["type"])
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await websocket.send(json.dumps({
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }))
    


async def run_signaling_server():
    async with websockets.serve(signaling_handler, "localhost", 8765):
        print("🟢 WebRTC signaling server running at ws://localhost:8765")
        await asyncio.Future()

async def send_message_to_client(message):
    global data_channel
    if data_channel and data_channel.readyState == "open":
        data_channel.send(json.dumps(message))
