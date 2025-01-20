import importlib

class DeviceManager:
    def __init__(self, devices_config):
        self.devices = self.load_devices(devices_config)

    def load_devices(self, devices_config):
        devices = {}
        for device_name, config in devices_config.items():
            module = importlib.import_module(config["module"])
            device_class = getattr(module, config["class"])
            devices[device_name] = device_class(config)
        return devices

    def execute_action(self, device_name, action):
        if device_name in self.devices:
            self.devices[device_name].execute(action)
        else:
            raise Exception(f"Device {device_name} not found.")
