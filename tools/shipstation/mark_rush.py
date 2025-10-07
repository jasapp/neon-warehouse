"""
Mark orders as RUSH in ShipStation

Functional approach:
- Search by order number or customer name
- Confirm before tagging
- Only tag orders awaiting shipment
"""

import os
import sys
from typing import Any, Optional
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(env_path)

API_BASE = "https://ssapi.shipstation.com"
API_KEY = os.getenv("SHIPSTATION_API_KEY")
API_SECRET = os.getenv("SHIPSTATION_API_SECRET")

# Import from existing tools
from .get_order import fetch_order as fetch_order_by_number
from .list_orders import fetch_orders, parse_order_summary


def find_order_by_number(order_number: str) -> Optional[dict[str, Any]]:
    """
    Find order by order number.

    Args:
        order_number: The order number to find

    Returns:
        Order dict or None if not found
    """
    try:
        return fetch_order_by_number(order_number)
    except Exception:
        return None


def find_orders_by_name(name: str) -> list[dict[str, Any]]:
    """
    Find orders by customer name (case-insensitive partial match).
    Only searches awaiting_shipment orders.

    Args:
        name: Customer name to search for

    Returns:
        List of matching order dicts
    """
    orders = fetch_orders(status="awaiting_shipment", page_size=500)
    name_lower = name.lower()

    matches = []
    for order in orders:
        customer_name = order.get("shipTo", {}).get("name", "")
        if customer_name and name_lower in customer_name.lower():
            matches.append(order)

    return matches


def get_tag_id(tag_name: str) -> Optional[int]:
    """
    Get tag ID by name.

    Args:
        tag_name: Name of the tag (case-insensitive)

    Returns:
        Tag ID or None if not found
    """
    if not API_KEY or not API_SECRET:
        return None

    auth = (API_KEY, API_SECRET)
    url = f"{API_BASE}/accounts/listtags"

    try:
        response = requests.get(url, auth=auth, timeout=10)
        response.raise_for_status()
        tags = response.json()

        # Look for tag (case-insensitive)
        tag_name_upper = tag_name.upper()
        for tag in tags:
            if tag.get("name", "").upper() == tag_name_upper:
                return tag.get("tagId")

        print(f"Tag '{tag_name}' not found. Please create it in ShipStation first.", file=sys.stderr)
        return None

    except Exception as e:
        print(f"Error fetching tags: {e}", file=sys.stderr)
        return None


def order_has_tag(order: dict[str, Any], tag_id: int) -> bool:
    """
    Check if an order already has a specific tag.

    Args:
        order: Order dict
        tag_id: Tag ID to check for

    Returns:
        True if order has the tag, False otherwise
    """
    tag_ids = order.get("tagIds") or []
    if not tag_ids:
        return False

    # tagIds can be list of ints or list of dicts with 'tagId' key
    if isinstance(tag_ids[0], dict):
        return any(t.get("tagId") == tag_id for t in tag_ids)
    else:
        return tag_id in tag_ids


def add_tag_to_order(order_id: int, tag_id: int, order_data: Optional[dict[str, Any]] = None) -> bool:
    """
    IO: Add a tag to an order (skips if already tagged).

    Args:
        order_id: The ShipStation order ID (not order number)
        tag_id: The tag ID to add
        order_data: Optional order dict to check existing tags (avoids extra API call)

    Returns:
        True if successful or already tagged, False otherwise
    """
    if not API_KEY or not API_SECRET:
        raise ValueError("ShipStation API credentials not configured.")

    # Check if order already has the tag
    if order_data and order_has_tag(order_data, tag_id):
        return True  # Already tagged, nothing to do

    auth = (API_KEY, API_SECRET)
    url = f"{API_BASE}/orders/addtag"

    payload = {
        "orderId": order_id,
        "tagId": tag_id
    }

    try:
        response = requests.post(url, auth=auth, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error adding tag: {e}", file=sys.stderr)
        return False


def add_rush_tag(order_id: int) -> bool:
    """
    Convenience wrapper: Add RUSH tag to an order.

    Args:
        order_id: The ShipStation order ID (not order number)

    Returns:
        True if successful, False otherwise
    """
    tag_id = get_tag_id("RUSH")
    if not tag_id:
        return False
    return add_tag_to_order(order_id, tag_id)


def confirm_action(order: dict[str, Any]) -> bool:
    """
    Show order details and ask for confirmation.

    Args:
        order: Order dict

    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n📦 Order #{order.get('orderNumber')}")

    ship_to = order.get("shipTo", {})
    customer_name = ship_to.get("name", "Unknown")
    customer_email = order.get("customerEmail", "")

    print(f"Customer: {customer_name} ({customer_email})")
    print(f"Status: {order.get('orderStatus')}")
    print(f"Total: ${order.get('orderTotal', 0):.2f}")

    items = order.get("items", [])
    if items:
        print(f"Items:")
        for item in items[:5]:  # Show first 5 items
            print(f"  - {item.get('name')} x{item.get('quantity')}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more items")

    print()
    response = input("Add RUSH tag to this order? (y/n): ").strip().lower()
    return response == 'y' or response == 'yes'


def select_order_from_list(orders: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """
    Show list of orders and let user select one.

    Args:
        orders: List of order dicts

    Returns:
        Selected order or None if cancelled
    """
    print(f"\nFound {len(orders)} matching orders:\n")

    for i, order in enumerate(orders, 1):
        ship_to = order.get("shipTo", {})
        customer_name = ship_to.get("name", "Unknown")
        customer_email = order.get("customerEmail", "")
        order_number = order.get("orderNumber")
        order_total = order.get("orderTotal", 0)

        print(f"{i}. #{order_number} - {customer_name} ({customer_email}) - ${order_total:.2f}")

    print()
    response = input("Select order number (or 'cancel'): ").strip()

    if response.lower() == 'cancel':
        return None

    try:
        index = int(response) - 1
        if 0 <= index < len(orders):
            return orders[index]
    except ValueError:
        pass

    print("Invalid selection.")
    return None


def mark_rush(query: str, confirm: bool = True) -> None:
    """
    Main function: Mark an order as RUSH.

    Args:
        query: Order number or customer name
        confirm: Whether to ask for confirmation
    """
    # Try as order number first
    if query.isdigit():
        order = find_order_by_number(query)

        if not order:
            print(f"Order #{query} not found.")
            return

        # Check if awaiting shipment
        if order.get("orderStatus") != "awaiting_shipment":
            status = order.get("orderStatus")
            print(f"Order #{query} has status '{status}' - can only rush orders awaiting shipment.")
            return

        # Check if already tagged
        tag_id = get_tag_id("RUSH")
        if tag_id and order_has_tag(order, tag_id):
            print(f"Order #{query} already has RUSH tag.")
            return

        # Confirm if needed
        if confirm and not confirm_action(order):
            print("Cancelled.")
            return

        # Add RUSH tag
        order_id = order.get("orderId")
        if add_tag_to_order(order_id, tag_id, order):
            print(f"✓ Added RUSH tag to order #{query}")
        else:
            print(f"✗ Failed to add RUSH tag to order #{query}")

    else:
        # Search by name
        orders = find_orders_by_name(query)

        if not orders:
            print(f"No orders found for '{query}' (awaiting shipment).")
            return

        # Single match - show and confirm
        if len(orders) == 1:
            order = orders[0]
            tag_id = get_tag_id("RUSH")

            # Check if already tagged
            if tag_id and order_has_tag(order, tag_id):
                order_number = order.get("orderNumber")
                print(f"Order #{order_number} already has RUSH tag.")
                return

            if confirm and not confirm_action(order):
                print("Cancelled.")
                return

            order_id = order.get("orderId")
            order_number = order.get("orderNumber")

            if add_tag_to_order(order_id, tag_id, order):
                print(f"✓ Added RUSH tag to order #{order_number}")
            else:
                print(f"✗ Failed to add RUSH tag to order #{order_number}")

        # Multiple matches - let user select
        else:
            order = select_order_from_list(orders)

            if not order:
                print("Cancelled.")
                return

            tag_id = get_tag_id("RUSH")

            # Check if already tagged
            if tag_id and order_has_tag(order, tag_id):
                order_number = order.get("orderNumber")
                print(f"Order #{order_number} already has RUSH tag.")
                return

            if confirm and not confirm_action(order):
                print("Cancelled.")
                return

            order_id = order.get("orderId")
            order_number = order.get("orderNumber")

            if add_tag_to_order(order_id, tag_id, order):
                print(f"✓ Added RUSH tag to order #{order_number}")
            else:
                print(f"✗ Failed to add RUSH tag to order #{order_number}")


def main() -> None:
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python -m tools.shipstation.mark_rush <order_number|customer_name> [--confirm=true|false]")
        sys.exit(1)

    query = sys.argv[1]
    confirm = True

    # Parse --confirm flag
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if arg.startswith("--confirm="):
                confirm_val = arg.split("=")[1].lower()
                confirm = confirm_val in ["true", "yes", "1"]

    try:
        mark_rush(query, confirm=confirm)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
