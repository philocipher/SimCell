# main.py

from controllers.simulator_controller import SimulatorController
from models.model import Model
from views.web_view import WebView
import time
import threading

def main():
    model = Model()
    # view = CLIView()
    view = WebView()
    controller = SimulatorController(model, view)
    
    # controller.load_gnbs()
    controller.load_ues()
    # controller.start()


    def loop():
        tick_rate = 0.1  # seconds
        while True:
            start_time = time.time()
            
            controller.run_simulation()
            
            elapsed = time.time() - start_time
            sleep_time = max(0, tick_rate - elapsed)
            
            # print(f"🕒 run_simulation() took {elapsed:.4f} seconds")
            time.sleep(sleep_time)

    threading.Thread(target=loop, daemon=True).start()


    print("🚀 App is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 App terminated.")


if __name__ == "__main__":
    main()
