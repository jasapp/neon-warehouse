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

Provides example CLI tools and custom queries using:
- **shipstation-mcp** - All core ShipStation operations now via MCP
- **Shopify** - inventory checks, product data (coming soon)

This repo now serves as:
- Example scripts for custom ShipStation queries
- Reference for using shipstation-mcp

**Design Philosophy:**
- Use shipstation-mcp for all core operations
- Keep custom business logic here (like DC2 email extraction)
- Simple CLI wrappers when needed

## Project Structure

```
neon-warehouse/
├── tools/
│   ├── shipstation/        # Uses shipstation-mcp
│   │   ├── __init__.py     # Re-exports from shipstation-mcp
│   │   └── get_dc2_emails.py  # Example custom query
│   └── shopify/            # Shopify tools (coming soon)
├── config/
│   └── .env.example        # Environment variables template
└── README.md
```

**Note:** Core ShipStation operations have moved to the `shipstation-mcp` package.

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
from tools.shipstation import get_order, find_order, mark_rush

# All functions now use shipstation-mcp
order = get_order("9471")
print(f"Order status: {order['orderStatus']}")

# Find orders
orders = find_order("John Smith")
print(f"Found {len(orders)} orders")

# Mark as rush
result = mark_rush("9471")
```

### Example: Custom Query
```bash
# Get DC2 customer emails
python -m tools.shipstation.get_dc2_emails
```

### With shipstation-mcp
All ShipStation operations now use the `shipstation-mcp` MCP server.
See https://github.com/jasapp/shipstation-mcp for details.

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

- [x] Core ShipStation operations moved to shipstation-mcp
- [x] Example custom queries (DC2 emails)
- [ ] Shopify: Draft order + send invoice
- [ ] Shopify: Check inventory
- [ ] Shopify: Get product details
- [ ] More example queries and CLI tools

## Contributing

It's just you and Claude for now. Keep functions small, add tests, document weird shit.

## License

Do whatever you want with it. MIT or public domain or whatever.

---

*Built with Python, functional programming principles, and a healthy disregard for enterprise bullshit.* 🔥
