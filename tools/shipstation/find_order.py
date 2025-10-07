"""
Shared order finding logic with fuzzy matching

Used by mark_rush, add_note, and warehouse commands.
"""

from typing import Any, Optional
from rapidfuzz import fuzz, process

from .get_order import fetch_order as fetch_order_by_number
from .list_orders import fetch_orders


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


def find_orders_by_name(name: str, fuzzy_threshold: int = 65) -> list[dict[str, Any]]:
    """
    Find orders by customer name with fuzzy matching.

    First tries exact substring match (case-insensitive).
    If no matches, falls back to fuzzy matching.

    Args:
        name: Customer name to search for
        fuzzy_threshold: Minimum similarity score (0-100) for fuzzy matches

    Returns:
        List of matching order dicts, sorted by relevance
    """
    orders = fetch_orders(status="awaiting_shipment", page_size=500)
    name_lower = name.lower()

    # First try exact substring matching
    exact_matches = []
    for order in orders:
        customer_name = order.get("shipTo", {}).get("name", "")
        if customer_name and name_lower in customer_name.lower():
            exact_matches.append(order)

    if exact_matches:
        return exact_matches

    # No exact matches - try fuzzy matching
    print(f"No exact match for '{name}', trying fuzzy search...")
    candidates = []
    for order in orders:
        customer_name = order.get("shipTo", {}).get("name", "")
        if customer_name:
            candidates.append((order, customer_name))

    if not candidates:
        return []

    # Use rapidfuzz to find similar names
    # Try multiple algorithms and take the best score
    fuzzy_matches = []
    for order, customer_name in candidates:
        name_clean = customer_name.lower()
        scores = [
            fuzz.partial_ratio(name_lower, name_clean),
            fuzz.token_sort_ratio(name_lower, name_clean),
            fuzz.WRatio(name_lower, name_clean)
        ]
        best_score = max(scores)
        if best_score >= fuzzy_threshold:
            fuzzy_matches.append((best_score, order))

    # Sort by similarity score (highest first)
    fuzzy_matches.sort(key=lambda x: x[0], reverse=True)

    return [order for score, order in fuzzy_matches]


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
