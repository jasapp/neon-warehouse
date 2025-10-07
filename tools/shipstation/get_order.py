"""
Get order information from ShipStation

Functional approach:
- parse_order: pure function to transform API response
- fetch_order: IO function to call API
- get_order_info: compose them together
"""

import os
from typing import Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables from root or config directory
from pathlib import Path
env_path = Path(__file__).parent.parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

API_BASE = "https://ssapi.shipstation.com"
API_KEY = os.getenv("SHIPSTATION_API_KEY")
API_SECRET = os.getenv("SHIPSTATION_API_SECRET")


def parse_order(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Pure function: Extract useful bits from ShipStation's response.

    Args:
        raw: Raw API response dict

    Returns:
        Cleaned order dict with relevant fields
    """
    # Safely handle tags - can be None or list of dicts/strings
    tags_raw = raw.get("tagIds") or raw.get("tags") or []
    if tags_raw and isinstance(tags_raw[0], dict):
        tags = [tag.get("name", "") for tag in tags_raw]
    else:
        tags = list(tags_raw) if isinstance(tags_raw, (list, tuple)) else []

    # Safely handle shipments
    shipments = raw.get("shipments", [])
    tracking_number = None
    carrier = None
    if shipments:
        tracking_number = shipments[0].get("trackingNumber")
        carrier = shipments[0].get("carrierCode")

    return {
        "order_id": raw.get("orderId"),
        "order_number": raw.get("orderNumber"),
        "order_key": raw.get("orderKey"),
        "order_status": raw.get("orderStatus"),
        "customer_email": raw.get("customerEmail"),
        "customer_name": raw.get("shipTo", {}).get("name"),
        "order_date": raw.get("orderDate"),
        "ship_date": raw.get("shipDate"),
        "tracking_number": tracking_number,
        "carrier": carrier,
        "tags": tags,
        "items": [
            {
                "name": item.get("name"),
                "sku": item.get("sku"),
                "quantity": item.get("quantity"),
            }
            for item in raw.get("items", [])
        ],
    }


def fetch_order(order_number: str) -> dict[str, Any]:
    """
    IO function: Get order from ShipStation API by order number.

    Args:
        order_number: The order number to look up

    Returns:
        Raw API response as dict

    Raises:
        ValueError: If API credentials not configured
        requests.HTTPError: If API request fails
    """
    if not API_KEY or not API_SECRET:
        raise ValueError("ShipStation API credentials not configured. Check .env file.")

    # ShipStation requires basic auth
    auth = (API_KEY, API_SECRET)

    # Search for orders by order number
    url = f"{API_BASE}/orders"
    params = {"orderNumber": order_number}

    response = requests.get(url, auth=auth, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    orders = data.get("orders", [])

    if not orders:
        raise ValueError(f"No order found with number: {order_number}")

    # Return first matching order
    return orders[0]


def get_order_info(order_number: str) -> dict[str, Any]:
    """
    Compose: Fetch and parse order information.

    Args:
        order_number: The order number to look up

    Returns:
        Parsed order information dict

    Example:
        >>> order = get_order_info("12345")
        >>> print(f"Status: {order['order_status']}")
    """
    return parse_order(fetch_order(order_number))


def main() -> None:
    """CLI entry point"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m tools.shipstation.get_order <order_number>")
        sys.exit(1)

    order_number = sys.argv[1]

    try:
        order = get_order_info(order_number)

        # Pretty print
        print(f"\n📦 Order #{order['order_number']}")
        print(f"Status: {order['order_status']}")
        if order.get('customer_name'):
            print(f"Customer: {order['customer_name']} ({order['customer_email']})")
        else:
            print(f"Customer: {order['customer_email']}")
        print(f"Order Date: {order['order_date']}")

        if order['tracking_number']:
            print(f"Tracking: {order['tracking_number']} ({order['carrier']})")

        if order['tags']:
            print(f"Tags: {', '.join(order['tags'])}")

        print(f"\nItems:")
        for item in order['items']:
            print(f"  - {item['name']} (SKU: {item['sku']}) x{item['quantity']}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
