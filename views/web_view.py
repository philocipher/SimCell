
import os
import webbrowser
import threading
import asyncio
import http.server
import socketserver
from .websocket_server import run_server, wait_for_client_and_send
import time
from .webrtc_server import run_signaling_server, send_message_to_client, data_channel_ready, register_virtual_time_callback, register_coord_callback

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

        register_virtual_time_callback(self.handle_received_virtual_time)
        register_coord_callback(self.handle_coords)



    def set_controller(self, controller):
            self.controller = controller

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

    def add_ue(self, ue):
        message = {
            "type": "add_ue",
            "id": ue.ue_id,
            "supi": ue.supi,
            "ambr_downlink": ue.ambr_downlink,
            "ambr_uplink": ue.ambr_uplink
            }
        asyncio.run_coroutine_threadsafe(
                send_message_to_client(message),
                self.async_loop
            )
         
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

    def kill_ue(self, ue_id):
        message = {
            "type": "kill_ue",
            "id": ue_id
            }
        asyncio.run_coroutine_threadsafe(
                send_message_to_client(message),
                self.async_loop
            )


    def show_ue_event_log(self, ue_id, event_log):
        message = {
            "type": "ue_event_log",
            "ue_id": ue_id,
            "timestamp": str(event_log.time),
            "event_type": event_log.event.type.name,
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
        
    def draw_line(self, a_lat, a_lon, b_lat, b_lon, ue_id=None, color="green"):
        color_map = {
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "orange": "#FFA500"
        }
        hex_color = color_map.get(color.lower(), "#00FF00")  # Default to green if unknown


        message = {
            "type": "draw_line",
            "a_lat": a_lat,
            "a_lon": a_lon,
            "b_lat": b_lat,
            "b_lon": b_lon,
            "ue_id": ue_id,
            "color": hex_color
        }
        asyncio.run_coroutine_threadsafe(
            send_message_to_client(message),
            self.async_loop
        )

    def handle_received_virtual_time(self, virtual_time):
        self.controller.set_virtual_time(virtual_time)


    def handle_coords(self, coords):
        self.controller.load_gnbs((coords[1], coords[3]) , (coords[0], coords[2]))