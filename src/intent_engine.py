import yaml

class IntentEngine:
    def __init__(self, config_file):
        self.intents = self.load_intents(config_file)

    def load_intents(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)["intents"]

    def process_trigger(self, trigger):
        for intent in self.intents:
            if self.matches(intent, trigger):
                print(f"Trigger matched intent: {intent['name']}")
                self.execute_actions(intent['actions'])

    def matches(self, intent, trigger):
        trigger_event = trigger.get("event")
        intent_trigger = intent["trigger"]
        return (
            intent_trigger["event"] == trigger_event and
            intent_trigger.get("token") == trigger.get("token")
        )

    def execute_actions(self, actions):
        for action in actions:
            print(f"Executing action: {action}")

if __name__ == "__main__":
    engine = IntentEngine("intents.yaml")
    test_trigger = {
        "event": "Transfer",
        "token": "0x1234567890abcdef1234567890abcdef12345678",
        "from": "0xabc123",
        "to": "0xdef456",
        "value": 1000
    }
    engine.process_trigger(test_trigger)
