"""
Tests for ShipStation tools

Using pytest with mocked API responses.
"""

import pytest
import responses
from tools.shipstation.get_order import parse_order, fetch_order, get_order_info


def test_parse_order_basic(sample_order):
    """Test parsing a basic order response"""
    parsed = parse_order(sample_order)

    assert parsed["order_id"] == 1234567
    assert parsed["order_number"] == "9999"
    assert parsed["order_status"] == "awaiting_shipment"
    assert parsed["customer_email"] == "test@example.com"
    assert parsed["customer_name"] == "Test Customer"
    assert len(parsed["items"]) == 2
    assert parsed["items"][0]["name"] == "Titanium DC2"
    assert parsed["items"][0]["quantity"] == 1
    assert parsed["tracking_number"] is None
    assert parsed["tags"] == []


def test_parse_order_with_tracking(sample_shipped_order):
    """Test parsing order with tracking info"""
    parsed = parse_order(sample_shipped_order)

    assert parsed["order_status"] == "shipped"
    assert parsed["tracking_number"] == "1Z999AA10123456784"
    assert parsed["carrier"] == "ups"


def test_parse_order_with_tags(sample_order_with_tags):
    """Test parsing order with tags"""
    parsed = parse_order(sample_order_with_tags)

    assert len(parsed["tags"]) == 1
    assert "RUSH" in parsed["tags"]


def test_parse_order_empty_response():
    """Test parsing minimal/empty response"""
    raw = {}
    parsed = parse_order(raw)

    assert parsed["order_id"] is None
    assert parsed["order_number"] is None
    assert parsed["items"] == []
    assert parsed["tags"] == []


@responses.activate
def test_fetch_order_success(sample_order):
    """Test fetching an order by number"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1},
        status=200
    )

    order = fetch_order("9999")

    assert order is not None
    assert order["orderNumber"] == "9999"
    assert order["orderId"] == 1234567


@responses.activate
def test_fetch_order_not_found():
    """Test fetching non-existent order"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [], "total": 0},
        status=200
    )

    with pytest.raises(ValueError, match="No order found"):
        fetch_order("99999")


@responses.activate
def test_get_order_info_integration(sample_order):
    """Test complete get_order_info flow"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1},
        status=200
    )

    order = get_order_info("9999")

    assert order["order_number"] == "9999"
    assert order["customer_name"] == "Test Customer"
    assert order["order_status"] == "awaiting_shipment"
    assert len(order["items"]) == 2
