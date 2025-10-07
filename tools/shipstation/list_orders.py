"""
List orders from ShipStation by status

Functional approach:
- parse_order_summary: pure function for lightweight order info
- fetch_orders: IO function to call API
- list_orders_by_status: compose them together
"""

import os
from typing import Any, Literal
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

OrderStatus = Literal[
    "awaiting_payment",
    "awaiting_shipment",
    "shipped",
    "on_hold",
    "cancelled",
]


def parse_order_summary(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Pure function: Extract summary info from order.

    Args:
        raw: Raw order dict from API

    Returns:
        Lightweight order summary
    """
    # Safely handle tags - can be None or list of dicts/strings
    tags_raw = raw.get("tagIds") or raw.get("tags") or []
    if tags_raw and isinstance(tags_raw[0], dict):
        tags = [tag.get("name", "") for tag in tags_raw]
    else:
        tags = list(tags_raw) if isinstance(tags_raw, (list, tuple)) else []

    # Get customer name from shipTo
    customer_name = raw.get("shipTo", {}).get("name")

    return {
        "order_number": raw.get("orderNumber"),
        "order_date": raw.get("orderDate"),
        "order_status": raw.get("orderStatus"),
        "customer_name": customer_name,
        "customer_email": raw.get("customerEmail"),
        "order_total": raw.get("orderTotal", 0.0),
        "items_count": len(raw.get("items", [])),
        "tags": tags,
    }


def fetch_orders(
    status: OrderStatus = "awaiting_shipment",
    page: int = 1,
    page_size: int = 500
) -> list[dict[str, Any]]:
    """
    IO function: Get orders from ShipStation API by status.

    Args:
        status: Order status to filter by
        page: Page number (starts at 1)
        page_size: Number of results per page (max 500)

    Returns:
        List of raw order dicts

    Raises:
        ValueError: If API credentials not configured
        requests.HTTPError: If API request fails
    """
    if not API_KEY or not API_SECRET:
        raise ValueError("ShipStation API credentials not configured. Check .env file.")

    auth = (API_KEY, API_SECRET)
    url = f"{API_BASE}/orders"

    params = {
        "orderStatus": status,
        "page": page,
        "pageSize": page_size,
    }

    response = requests.get(url, auth=auth, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    # Debug: print response if no orders key
    if "orders" not in data:
        print(f"DEBUG - API Response keys: {data.keys()}")
        print(f"DEBUG - Full response: {data}")

    return data.get("orders", [])


def list_orders_by_status(
    status: OrderStatus = "awaiting_shipment",
    limit: int = 500
) -> list[dict[str, Any]]:
    """
    Compose: Fetch and parse order summaries.

    Args:
        status: Order status to filter by
        limit: Max number of orders to return

    Returns:
        List of parsed order summaries

    Example:
        >>> orders = list_orders_by_status("awaiting_shipment")
        >>> print(f"Found {len(orders)} orders")
    """
    raw_orders = fetch_orders(status=status, page_size=limit)
    return [parse_order_summary(order) for order in raw_orders]


def main() -> None:
    """CLI entry point"""
    import sys

    status: OrderStatus = "awaiting_shipment"

    if len(sys.argv) > 1:
        status = sys.argv[1]  # type: ignore

    try:
        orders = list_orders_by_status(status)

        print(f"\n📦 Orders with status: {status}")
        print(f"Found {len(orders)} orders\n")

        if not orders:
            print("No orders found.")
            return

        for order in orders:
            tags_str = f" [{', '.join(order['tags'])}]" if order['tags'] else ""
            print(f"#{order['order_number']}{tags_str}")

            # Show name if available, otherwise just email
            if order.get('customer_name'):
                print(f"  Customer: {order['customer_name']} ({order['customer_email']})")
            else:
                print(f"  Customer: {order['customer_email']}")

            print(f"  Total: ${order['order_total']:.2f}")
            print(f"  Items: {order['items_count']}")
            print(f"  Date: {order['order_date']}")
            print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
