from src.base_intent import BaseIntent
import logging

logger = logging.getLogger(__name__)

class DaiMonitor(BaseIntent):
    def process_event(self, event):
        logger.info(f"DAI Transfer detected: {event['args']}")
        actions = self.intent_config["actions"]
        for action in actions:
            device_name = action["device"]
            self.device_manager.execute_action(device_name, action)
