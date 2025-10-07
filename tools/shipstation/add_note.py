"""
Add internal notes to ShipStation orders

Functional approach:
- Search by order number or customer name
- Confirm before adding note
- Append to existing internal notes (comma-separated)
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
from .mark_rush import get_tag_id, add_tag_to_order
from .find_order import find_order_by_number, find_orders_by_name, select_order_from_list


def update_order_notes(order: dict[str, Any], new_note: str) -> bool:
    """
    IO: Update internal notes for an order.
    Appends new note to existing notes (comma-separated).

    Args:
        order: Full order dict from ShipStation
        new_note: The note to append

    Returns:
        True if successful, False otherwise
    """
    if not API_KEY or not API_SECRET:
        raise ValueError("ShipStation API credentials not configured.")

    auth = (API_KEY, API_SECRET)
    url = f"{API_BASE}/orders/createorder"

    # Append to existing notes with comma separator
    existing_notes = order.get("internalNotes", "")
    if existing_notes:
        combined_notes = f"{existing_notes}, {new_note}"
    else:
        combined_notes = new_note

    # Update the order dict with new notes
    updated_order = order.copy()
    updated_order["internalNotes"] = combined_notes

    try:
        response = requests.post(url, auth=auth, json=updated_order, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error updating notes: {e}", file=sys.stderr)
        return False


def confirm_action(order: dict[str, Any], note: str) -> bool:
    """
    Show order details and note preview, ask for confirmation.

    Args:
        order: Order dict
        note: The note to be added

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

    existing_notes = order.get("internalNotes", "")
    if existing_notes:
        print(f"\nCurrent notes: {existing_notes}")
        print(f"New notes will be: {existing_notes}, {note}")
    else:
        print(f"\nNew notes: {note}")

    print()
    response = input(f"Add this note to order? (y/n): ").strip().lower()
    return response == 'y' or response == 'yes'


def add_note(query: str, note: str, confirm: bool = True) -> None:
    """
    Main function: Add internal note to an order.

    Args:
        query: Order number or customer name
        note: The note to add
        confirm: Whether to ask for confirmation
    """
    # Try as order number first
    if query.isdigit():
        order = find_order_by_number(query)

        if not order:
            print(f"Order #{query} not found.")
            return

        # Confirm if needed
        if confirm and not confirm_action(order, note):
            print("Cancelled.")
            return

        # Update notes
        order_number = order.get("orderNumber")
        order_id = order.get("orderId")

        # Add Special NOTE! tag
        tag_id = get_tag_id("Special NOTE!")
        if tag_id:
            add_tag_to_order(order_id, tag_id, order)

        if update_order_notes(order, note):
            print(f"✓ Added note to order #{order_number}")
        else:
            print(f"✗ Failed to add note to order #{order_number}")

    else:
        # Search by name
        orders = find_orders_by_name(query)

        if not orders:
            print(f"No orders found for '{query}' (awaiting shipment).")
            return

        # Single match - show and confirm
        if len(orders) == 1:
            order = orders[0]

            if confirm and not confirm_action(order, note):
                print("Cancelled.")
                return

            order_number = order.get("orderNumber")
            order_id = order.get("orderId")

            # Add Special NOTE! tag
            tag_id = get_tag_id("Special NOTE!")
            if tag_id:
                add_tag_to_order(order_id, tag_id, order)

            if update_order_notes(order, note):
                print(f"✓ Added note to order #{order_number}")
            else:
                print(f"✗ Failed to add note to order #{order_number}")

        # Multiple matches - let user select
        else:
            order = select_order_from_list(orders)

            if not order:
                print("Cancelled.")
                return

            if confirm and not confirm_action(order, note):
                print("Cancelled.")
                return

            order_number = order.get("orderNumber")
            order_id = order.get("orderId")

            # Add Special NOTE! tag
            tag_id = get_tag_id("Special NOTE!")
            if tag_id:
                add_tag_to_order(order_id, tag_id, order)

            if update_order_notes(order, note):
                print(f"✓ Added note to order #{order_number}")
            else:
                print(f"✗ Failed to add note to order #{order_number}")


def main() -> None:
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Usage: python -m tools.shipstation.add_note <order_number|customer_name> <note>")
        sys.exit(1)

    query = sys.argv[1]
    note = sys.argv[2]
    confirm = True

    # Parse --confirm flag
    if len(sys.argv) > 3:
        for arg in sys.argv[3:]:
            if arg.startswith("--confirm="):
                confirm_val = arg.split("=")[1].lower()
                confirm = confirm_val in ["true", "yes", "1"]

    try:
        add_note(query, note, confirm=confirm)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
