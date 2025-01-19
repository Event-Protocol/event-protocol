from gpiozero import LED, Device
from gpiozero.pins.mock import MockFactory
from src.action_module import ActionModule

# Set the pin factory to MockFactory
Device.pin_factory = MockFactory()

class RaspberryPicoModule(ActionModule):
    def __init__(self):
        self.led = LED(17)  # Simulate GPIO pin 17

    def execute(self, action):
        if action["state"] == "on":
            self.led.on()
            print("Raspberry Pico: LED turned ON")
        elif action["state"] == "off":
            self.led.off()
            print("Raspberry Pico: LED turned OFF")
