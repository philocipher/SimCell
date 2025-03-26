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
    
    controller.load_gnbs()
    controller.load_ues()
    # controller.start()


    def loop():
        while True:
            controller.run_simulation()
            time.sleep(0.1)  # Adjust the simulation tick rate (1s)

    threading.Thread(target=loop, daemon=True).start()


    print("🚀 App is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 App terminated.")


if __name__ == "__main__":
    main()
