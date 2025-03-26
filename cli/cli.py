class CLI:
    def __init__(self, controller):
        self.controller = controller
    
    def run(self):
        while True:
            command = input("Enter command (start/stop/speed/exit): ")
            if command == "start":
                self.controller.start()
                print("Simulation started.")
            elif command == "stop":
                self.controller.stop()
                print("Simulation stopped.")
            elif command.startswith("speed"):
                _, speed = command.split()
                self.controller.set_speed(int(speed))
                print(f"Speed set to {speed}x.")
            elif command == "exit":
                self.controller.stop()
                break