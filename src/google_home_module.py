import requests
from src.action_module import ActionModule

class GoogleHomeModule(ActionModule):
    def execute(self, action):
        url = "https://googlehome.local/command"
        payload = {"command": action["command"]}
        try:
            response = requests.post(url, json=payload)
            print(f"Google Home: Response {response.status_code}")
        except Exception as e:
            print(f"Google Home: Failed to send command - {e}")
