# neon-warehouse 📦✨

**Administrative assistant tooling for order fulfillment and inventory management.**

Built to automate the boring shit so you can focus on building cool flashlights.

---

## 🤖 Note to Future Claude Sessions

When working on this project:
- **Keep it functional** - small pure functions, compose them
- **Be chill and direct** - no corporate bullshit
- **Think like a Lisp hacker** - data transformation pipelines, not OOP hierarchies
- **Log everything** - structured logs for debugging, plain text for humans

The user is an ex-Lisp/Clojure dev who values simplicity and elegance. Keep functions small, side effects explicit.

---

## What This Does

Provides tools for Claude (and humans) to interact with:
- **ShipStation** - order management, tracking, rush orders
- **Shopify** - inventory checks, product data
- **More to come** - whatever else needs automating

**Design Philosophy:**
- Small, composable functions
- Pure functions for data transformation
- IO/side effects isolated and explicit
- Good logging and error handling
- Usable as CLI tools or library functions

## Project Structure

```
neon-warehouse/
├── tools/
│   ├── shipstation/        # ShipStation API tools
│   ├── shopify/            # Shopify API tools
│   └── __init__.py
├── tests/                  # Unit tests
├── docs/                   # API documentation
├── config/
│   └── .env.example        # Environment variables template
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Modern Python package config
└── README.md
```

## Installation

```bash
cd ~/src/neon-warehouse
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your API credentials.

## Usage

### As Library
```python
from tools.shipstation import get_order_info

order = get_order_info("12345")
print(f"Order status: {order['order_status']}")
```

### As CLI
```bash
python -m tools.shipstation.get_order 12345
```

### With Claude
Just ask! Claude has access to these tools and can:
- Check order status
- Mark orders as rush
- Check inventory levels
- And more...

## Development

### Running Tests
```bash
pytest tests/
```

### Type Checking
```bash
mypy tools/
```

### Logging

Logs are structured JSON (for parsing) and pretty console output (for humans).

Log files: `~/.neon-warehouse/logs/`

Configuration coming soon - will include Notion integration for persistent logs.

## API Credentials

You'll need:
- **ShipStation**: API Key + API Secret (Settings → API Settings)
- **Shopify**: Admin API token (Apps → Develop apps)

Store them in `.env` file (never commit this!).

## Roadmap

- [x] Project structure
- [x] ShipStation: Get order info
- [x] ShipStation: Mark order as rush (with idempotency)
- [x] ShipStation: List orders by status
- [x] Generic tag management (any tag, not just RUSH)
- [ ] Shopify: Check inventory
- [ ] Shopify: Get product details
- [ ] Logging infrastructure (console + file + Notion)
- [ ] Unit tests with mocked APIs
- [ ] Sandbox/test environment setup
- [ ] CLI interface improvements
- [ ] Documentation

## Contributing

It's just you and Claude for now. Keep functions small, add tests, document weird shit.

## License

Do whatever you want with it. MIT or public domain or whatever.

---

*Built with Python, functional programming principles, and a healthy disregard for enterprise bullshit.* 🔥
