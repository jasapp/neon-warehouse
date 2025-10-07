"""
Unified warehouse command - auto-detects intent from context

Usage:
  warehouse "Noah Wolfe" "RUSH"           → adds RUSH tag
  warehouse "Noah Wolfe" "no memory"      → adds Special NOTE! tag + internal note
  warehouse "9219" "check battery"        → adds Special NOTE! tag + internal note
"""

import sys
from .mark_rush import mark_rush
from .add_note import add_note


def warehouse_command(query: str, action: str, confirm: bool = True) -> None:
    """
    Auto-detect intent and route to appropriate function.

    Args:
        query: Order number or customer name
        action: Either "RUSH" or a note to add
        confirm: Whether to ask for confirmation
    """
    # Detect RUSH (case-insensitive)
    if action.upper() == "RUSH":
        mark_rush(query, confirm=confirm)
    else:
        # Everything else is a special note
        add_note(query, action, confirm=confirm)


def main() -> None:
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Usage: warehouse <order_number|customer_name> <action>")
        print()
        print("Examples:")
        print("  warehouse \"Noah Wolfe\" \"RUSH\"")
        print("  warehouse \"Noah Wolfe\" \"no memory\"")
        print("  warehouse 9219 \"check battery\"")
        sys.exit(1)

    query = sys.argv[1]
    action = sys.argv[2]
    confirm = True

    # Parse --confirm flag
    if len(sys.argv) > 3:
        for arg in sys.argv[3:]:
            if arg.startswith("--confirm="):
                confirm_val = arg.split("=")[1].lower()
                confirm = confirm_val in ["true", "yes", "1"]

    try:
        warehouse_command(query, action, confirm=confirm)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
