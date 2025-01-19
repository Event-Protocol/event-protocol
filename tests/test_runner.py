import sys
import os
import yaml
from src.intent_engine import IntentEngine
from src.device_manager import DeviceManager

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, project_root)

# Define the paths for configuration files
modules_file_path = os.path.join(project_root, "modules.yaml")
intents_file_path = os.path.join(project_root, "intents.yaml")

# Load modules configuration
with open(modules_file_path, "r") as file:
    module_configs = yaml.safe_load(file)["modules"]

# Initialize device manager and intent engine
device_manager = DeviceManager(module_configs)
engine = IntentEngine(intents_file_path, device_manager)

# Simulate a trigger
test_trigger = {
    "event": "TestEvent"
}

# Process the trigger
print("Simulating TestEvent...")
engine.process_trigger(test_trigger)
