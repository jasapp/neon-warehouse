"""
Tests for list_orders module
"""

import pytest
import responses
from tools.shipstation.list_orders import (
    parse_order_summary,
    fetch_orders,
    list_orders_by_status
)


def test_parse_order_summary_basic(sample_order):
    """Test parsing order summary"""
    summary = parse_order_summary(sample_order)

    assert summary["order_number"] == "9999"
    assert summary["order_status"] == "awaiting_shipment"
    assert summary["customer_name"] == "Test Customer"
    assert summary["customer_email"] == "test@example.com"
    assert summary["order_total"] == 599.00
    assert summary["items_count"] == 2
    assert summary["tags"] == []


def test_parse_order_summary_with_tags(sample_order_with_tags):
    """Test parsing order summary with tags"""
    summary = parse_order_summary(sample_order_with_tags)

    assert summary["order_number"] == "9998"
    assert len(summary["tags"]) == 1
    assert "RUSH" in summary["tags"]


def test_parse_order_summary_no_name():
    """Test parsing order with no customer name"""
    order = {
        "orderNumber": "1234",
        "orderStatus": "awaiting_shipment",
        "customerEmail": "test@example.com",
        "orderDate": "2025-10-08T10:00:00",
        "orderTotal": 100.0,
        "items": [],
        "shipTo": {}  # No name field
    }

    summary = parse_order_summary(order)

    assert summary["customer_name"] is None
    assert summary["customer_email"] == "test@example.com"


@responses.activate
def test_fetch_orders_success(sample_orders_list):
    """Test fetching orders by status"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json=sample_orders_list,
        status=200
    )

    orders = fetch_orders(status="awaiting_shipment", page_size=10)

    assert len(orders) == 2
    assert orders[0]["orderNumber"] == "9999"
    assert orders[1]["orderNumber"] == "9996"


@responses.activate
def test_fetch_orders_empty():
    """Test fetching when no orders exist"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [], "total": 0},
        status=200
    )

    orders = fetch_orders(status="awaiting_shipment")

    assert orders == []


@responses.activate
def test_list_orders_by_status(sample_orders_list):
    """Test complete list_orders_by_status flow"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json=sample_orders_list,
        status=200
    )

    summaries = list_orders_by_status("awaiting_shipment", limit=10)

    assert len(summaries) == 2
    assert summaries[0]["order_number"] == "9999"
    assert summaries[0]["customer_name"] == "Test Customer"
    assert summaries[1]["order_number"] == "9996"
    assert summaries[1]["customer_name"] == "Second Customer"
