import importlib

class DeviceManager:
    def __init__(self, module_configs):
        self.modules = self.load_modules(module_configs)

    def load_modules(self, module_configs):
        modules = {}
        for config in module_configs:
            module_name = config["module"]
            class_name = config["class"]
            try:
                module = importlib.import_module(module_name)
                module_class = getattr(module, class_name)
                modules[config["name"]] = module_class()
            except Exception as e:
                print(f"Failed to load module {module_name}.{class_name}: {e}")
        return modules

    def execute_action(self, device_name, action):
        if device_name in self.modules:
            self.modules[device_name].execute(action)
        else:
            print(f"No module found for device: {device_name}")
