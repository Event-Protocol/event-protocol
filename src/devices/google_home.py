class GoogleHome:
    def __init__(self, config):
        self.ip = config["ip"]

    def execute(self, action):
        command = action.get("command")
        print(f"Sending command to Google Home ({self.ip}): {command}")
