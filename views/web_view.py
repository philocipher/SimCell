
import os
import webbrowser
import threading
import asyncio
import http.server
import socketserver
from .websocket_server import run_server, wait_for_client_and_send
import time
from .webrtc_server import run_signaling_server, send_message_to_client, data_channel_ready

class WebView:
    def __init__(self, udp_port=None, tcp_port=None):
        self.udp_port = udp_port
        self.tcp_port = tcp_port

        # Create a separate asyncio loop for signaling
        self.async_loop = asyncio.new_event_loop()

        self.open_browser()
        threading.Thread(target=self.start_websocket, daemon=True).start()
        threading.Thread(target=self.serve_files, daemon=True).start()

        # Start background threads
        threading.Thread(target=self.start_async_loop, daemon=True).start()
        print("⏳ Waiting for data channel to be ready...")
        self.block_until_data_channel_ready()
        print("✅ Data channel is ready!")



    def block_until_data_channel_ready(self):
            # Block in a temporary loop until the async event is set
            future = asyncio.run_coroutine_threadsafe(
                data_channel_ready.wait(), self.async_loop
            )
            # This will block until the coroutine completes
            future.result()  # Blocks until data_channel_ready is set

    def serve_files(self):
        handler = http.server.SimpleHTTPRequestHandler
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            print("📡 HTTP server running at http://localhost:8000")
            httpd.serve_forever()

    def start_websocket(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())

    def open_browser(self):
        webbrowser.open("http://localhost:8000/web_ui/index.html")

    def start_async_loop(self):
        asyncio.set_event_loop(self.async_loop)
        self.async_loop.run_until_complete(run_signaling_server())


    def move_ue(self, ue_id, new_lat, new_lon):
        message = {
            "type": "move_ue",
            "id": ue_id,
            "lat": new_lat,
            "lon": new_lon
        }
        asyncio.run_coroutine_threadsafe(
                send_message_to_client(message),
                self.async_loop
            )
        
    def place_gnb(self, gnb_id, new_lat, new_lon):
        message = {
            "type": "place_gnb",
            "id": gnb_id,
            "lat": new_lat,
            "lon": new_lon
        }
        asyncio.run_coroutine_threadsafe(
                    send_message_to_client(message),
                    self.async_loop
                )