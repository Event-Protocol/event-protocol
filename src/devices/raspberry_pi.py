class RaspberryPi:
    def __init__(self, config):
        self.pin = config["pin"]

    def execute(self, action):
        state = action.get("state")
        if state == "on":
            print(f"Turning on LED on pin {self.pin}")
        elif state == "off":
            print(f"Turning off LED on pin {self.pin}")
        else:
            print(f"Unknown action: {state}")
