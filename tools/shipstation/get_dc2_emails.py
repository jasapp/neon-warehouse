"""
Extract emails from awaiting_shipment orders containing DC2 products

Example of using shipstation-mcp for custom queries.
"""

import sys
sys.path.insert(0, '/home/jasapp/src/shipstation-mcp/src')

from shipstation_mcp.core.operations import list_orders


def has_dc2_product(order: dict) -> bool:
    """Check if order contains a DC2 product"""
    items = order.get("items", [])
    for item in items:
        sku = (item.get("sku") or "").upper()
        name = (item.get("name") or "").upper()

        # Check for DC2 in SKU or product name
        if "DC2" in sku or "DC2" in name:
            return True

    return False


def main() -> None:
    """Main entry point"""
    try:
        print("Fetching awaiting_shipment orders...")
        orders = list_orders(status="awaiting_shipment", limit=500)
        print(f"Found {len(orders)} total orders with awaiting_shipment status\n")

        # Filter for DC2 orders
        dc2_orders = [order for order in orders if has_dc2_product(order)]
        print(f"Found {len(dc2_orders)} orders containing DC2 products\n")

        # Extract unique emails
        emails = set()
        for order in dc2_orders:
            email = order.get("customerEmail")
            if email:
                emails.add(email)

        # Format for Gmail (comma-separated)
        email_list = ", ".join(sorted(emails))

        print("=" * 60)
        print("EMAILS FOR GMAIL (copy the line below):")
        print("=" * 60)
        print(email_list)
        print("=" * 60)
        print(f"\nTotal unique email addresses: {len(emails)}")

    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
