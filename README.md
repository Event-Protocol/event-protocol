# The Event Protocol

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-alpha-orange)

The Event Protocol is a modular, developer-friendly platform that bridges blockchain events with real-world actions through IoT devices and APIs. By connecting on-chain activity to physical devices and digital services, we enable a new generation of decentralized automation.

## 🌟 Core Features

- **Event Monitoring**: Listen to any on-chain event (transfers, governance, custom contracts)
- **Modular Architecture**: Easy-to-extend system for adding new devices and event handlers
- **Multi-Chain Support**: Compatible with Ethereum, Optimism, Polygon, and other EVM chains
- **Device Integrations**: Support for IoT devices like Raspberry Pi, Google Home, and more
- **Developer-First**: Simple YAML configurations and intuitive Python interfaces

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- An Ethereum node URL (e.g., Infura endpoint)
- Etherscan API key for ABI fetching

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/event-protocol.git
cd event-protocol
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials:
# INFURA_URL=your_infura_url
# ETHERSCAN_API_KEY=your_etherscan_key
```

### Basic Usage

1. Run the test runner:
```bash
python tests/test_runner.py
```

2. Enter the contract address when prompted
3. Select an event to monitor
4. Watch as blockchain events trigger your configured actions!

## 🏗️ Architecture

The Event Protocol follows a modular, plugin-based architecture:

### Core Components

- **Intent Engine**: Manages event detection and routing
- **Device Manager**: Handles device registration and action execution
- **Base Intent**: Template class for creating new event handlers
- **Device Modules**: Pluggable device integrations

### Project Structure
```
event-protocol/
├── src/
│   ├── base_intent.py        # Base class for intents
│   ├── devices/              # Device integrations
│   │   ├── raspberry_pi.py
│   │   ├── google_home.py
│   ├── intents/             # Event handlers
│   │   ├── dai_monitor/     
│   │   │   ├── dai_monitor.py
│   │   │   ├── intent.yaml
│   ├── intent_engine.py     # Core event processing
│   ├── device_manager.py    # Device orchestration
├── modules.yaml             # Device configuration
├── tests/
    └── test_runner.py       # Test harness
```

## 📚 Creating Your Own Modules

### Creating a New Device

1. Create a new Python file in `src/devices/`:

```python
class MyDevice:
    def __init__(self, config):
        self.config = config
        # Initialize device-specific settings

    def execute(self, action):
        # Implement device-specific action logic
        print(f"Executing action: {action}")
```

2. Add device configuration to `modules.yaml`:

```yaml
modules:
  my_device:
    module: src.devices.my_device
    class: MyDevice
    config:
      # Device-specific configuration
```

### Creating a New Intent

1. Create a new directory in `src/intents/`:
```bash
mkdir src/intents/my_intent
```

2. Create `intent.yaml`:
```yaml
name: MyIntent
module: my_intent
trigger:
  event: Transfer
  contract_address: "dynamic"
actions:
  - device: my_device
    state: "on"
```

3. Create the intent handler:
```python
from src.base_intent import BaseIntent

class MyIntent(BaseIntent):
    def process_event(self, event):
        # Process the blockchain event
        actions = self.intent_config["actions"]
        for action in actions:
            device_name = action["device"]
            self.device_manager.execute_action(device_name, action)
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation as needed
- Keep modules focused and single-purpose
- Use meaningful commit messages

## 📖 Documentation

For detailed documentation, visit our [documentation site](https://docs.eventprotocol.io).

Key documentation sections:
- [Architecture Overview](https://docs.eventprotocol.io/architecture)
- [Device Integration Guide](https://docs.eventprotocol.io/devices)
- [Intent Creation Tutorial](https://docs.eventprotocol.io/intents)
- [API Reference](https://docs.eventprotocol.io/api)


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ by the Event Protocol team
- Thanks to our amazing contributors
- Inspired by the blockchain and IoT communities

## 🤔 Questions?

- Check out our [FAQ](https://docs.eventprotocol.io/faq)
- Join our [Discord](https://discord.gg/eventprotocol)
- Open an [Issue](https://github.com/yourusername/event-protocol/issues)

---

Built with 🌟 by the blockchain community, for the blockchain community.