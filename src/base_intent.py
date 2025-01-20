class BaseIntent:
    def __init__(self, intent_config, device_manager, web3_instance):
        self.intent_config = intent_config
        self.device_manager = device_manager
        self.web3 = web3_instance

    def process_event(self, event):
        """
        Process an event trigger. Must be implemented by derived intents.
        """
        raise NotImplementedError("process_event must be implemented by the intent.")
