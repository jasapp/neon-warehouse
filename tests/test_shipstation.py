"""
Tests for ShipStation tools

Using pytest with mocked API responses.
"""

import pytest
from tools.shipstation.get_order import parse_order, get_order_info


def test_parse_order_basic():
    """Test parsing a basic order response"""
    raw = {
        "orderId": 12345,
        "orderNumber": "ORDER-001",
        "orderKey": "abc123",
        "orderStatus": "awaiting_shipment",
        "customerEmail": "customer@example.com",
        "orderDate": "2025-10-08T10:00:00",
        "shipDate": None,
        "items": [
            {
                "name": "Flashlight X",
                "sku": "FL-X-001",
                "quantity": 2,
            }
        ],
        "tagIds": [],
        "shipments": [],
    }

    parsed = parse_order(raw)

    assert parsed["order_id"] == 12345
    assert parsed["order_number"] == "ORDER-001"
    assert parsed["order_status"] == "awaiting_shipment"
    assert parsed["customer_email"] == "customer@example.com"
    assert len(parsed["items"]) == 1
    assert parsed["items"][0]["name"] == "Flashlight X"
    assert parsed["items"][0]["quantity"] == 2


def test_parse_order_with_tracking():
    """Test parsing order with tracking info"""
    raw = {
        "orderId": 12346,
        "orderNumber": "ORDER-002",
        "orderKey": "def456",
        "orderStatus": "shipped",
        "customerEmail": "customer2@example.com",
        "orderDate": "2025-10-08T10:00:00",
        "shipDate": "2025-10-08T14:00:00",
        "items": [],
        "tagIds": [{"name": "rush"}],
        "shipments": [
            {
                "trackingNumber": "1Z999AA10123456784",
                "carrierCode": "ups",
            }
        ],
    }

    parsed = parse_order(raw)

    assert parsed["order_status"] == "shipped"
    assert parsed["tracking_number"] == "1Z999AA10123456784"
    assert parsed["carrier"] == "ups"
    assert "rush" in parsed["tags"]


def test_parse_order_empty_response():
    """Test parsing minimal/empty response"""
    raw = {}
    parsed = parse_order(raw)

    assert parsed["order_id"] is None
    assert parsed["order_number"] is None
    assert parsed["items"] == []
    assert parsed["tags"] == []


# Integration tests would go here with responses library to mock HTTP
# Example:
# @responses.activate
# def test_fetch_order():
#     responses.add(
#         responses.GET,
#         "https://ssapi.shipstation.com/orders",
#         json={"orders": [...]},
#         status=200
#     )
#     order = fetch_order("ORDER-001")
#     assert order is not None
