import unittest
from src.device_manager import DeviceManager

class TestDeviceManager(unittest.TestCase):
    def setUp(self):
        self.module_configs = [
            {"name": "test_device", "module": "src.test_module", "class": "TestModule"}
        ]
        self.device_manager = DeviceManager(self.module_configs)

    def test_load_modules(self):
        self.assertIn("test_device", self.device_manager.modules)

    def test_execute_action(self):
        action = {"state": "on"}
        self.device_manager.execute_action("test_device", action)

if __name__ == "__main__":
    unittest.main()
