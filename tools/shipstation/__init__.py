"""
ShipStation tools - now powered by shipstation-mcp

All core ShipStation operations now use the shipstation-mcp package.
"""

# Import from shipstation-mcp
import sys
sys.path.insert(0, '/home/jasapp/src/shipstation-mcp/src')

from shipstation_mcp.core.operations import (
    find_order,
    get_order,
    list_orders,
    mark_rush,
    add_note,
    get_tag_list,
)

# Re-export for backwards compatibility
__all__ = [
    "find_order",
    "get_order",
    "list_orders",
    "mark_rush",
    "add_note",
    "get_tag_list",
]
