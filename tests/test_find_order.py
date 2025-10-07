"""
Tests for find_order module with fuzzy matching
"""

import pytest
import responses
from tools.shipstation.find_order import (
    find_order_by_number,
    find_orders_by_name,
    select_order_from_list
)


@responses.activate
def test_find_order_by_number_success(sample_order):
    """Test finding order by number"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1},
        status=200
    )

    order = find_order_by_number("9999")
    assert order is not None
    assert order["orderNumber"] == "9999"


@responses.activate
def test_find_order_by_number_not_found():
    """Test finding non-existent order"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [], "total": 0},
        status=200
    )

    order = find_order_by_number("99999")
    assert order is None


@responses.activate
def test_find_orders_by_name_exact_match(sample_order):
    """Test exact substring match"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1, "page": 1, "pages": 1},
        status=200
    )

    orders = find_orders_by_name("Test Customer")
    assert len(orders) == 1
    assert orders[0]["orderNumber"] == "9999"


@responses.activate
def test_find_orders_by_name_partial_match(sample_order):
    """Test partial substring match"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1, "page": 1, "pages": 1},
        status=200
    )

    # Should match "Test Customer" with "Test"
    orders = find_orders_by_name("Test")
    assert len(orders) == 1
    assert orders[0]["orderNumber"] == "9999"


@responses.activate
def test_find_orders_by_name_case_insensitive(sample_order):
    """Test case-insensitive matching"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1, "page": 1, "pages": 1},
        status=200
    )

    orders = find_orders_by_name("test customer")
    assert len(orders) == 1

    orders = find_orders_by_name("TEST CUSTOMER")
    assert len(orders) == 1


@responses.activate
def test_find_orders_by_name_fuzzy_match():
    """Test fuzzy matching with typos"""
    typo_order = {
        "orderId": 1234567,
        "orderNumber": "9999",
        "orderStatus": "awaiting_shipment",
        "customerEmail": "test@example.com",
        "shipTo": {"name": "Noah Wolfe"},
        "orderTotal": 579.00,
        "items": [],
        "tagIds": [],
        "shipments": []
    }

    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [typo_order], "total": 1, "page": 1, "pages": 1},
        status=200
    )

    # Should fuzzy match "noha" to "Noah Wolfe"
    orders = find_orders_by_name("noha")
    assert len(orders) == 1
    assert orders[0]["orderNumber"] == "9999"


@responses.activate
def test_find_orders_by_name_fuzzy_no_match():
    """Test fuzzy matching with string too different"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [
            {
                "orderId": 1,
                "orderNumber": "9999",
                "orderStatus": "awaiting_shipment",
                "shipTo": {"name": "John Smith"},
                "orderTotal": 100,
                "items": [],
                "tagIds": []
            }
        ], "total": 1, "page": 1, "pages": 1},
        status=200
    )

    # "xyz" should not match "John Smith" (score too low)
    orders = find_orders_by_name("xyz")
    assert orders == []


@responses.activate
def test_find_orders_by_name_multiple_fuzzy_matches():
    """Test fuzzy matching returns multiple similar names"""
    orders_data = {
        "orders": [
            {
                "orderId": 1,
                "orderNumber": "9001",
                "orderStatus": "awaiting_shipment",
                "shipTo": {"name": "Noah Wolfe"},
                "orderTotal": 100,
                "items": [],
                "tagIds": []
            },
            {
                "orderId": 2,
                "orderNumber": "9002",
                "orderStatus": "awaiting_shipment",
                "shipTo": {"name": "Noah Whitnah"},
                "orderTotal": 200,
                "items": [],
                "tagIds": []
            },
            {
                "orderId": 3,
                "orderNumber": "9003",
                "orderStatus": "awaiting_shipment",
                "shipTo": {"name": "Nolan Cook"},
                "orderTotal": 300,
                "items": [],
                "tagIds": []
            }
        ],
        "total": 3,
        "page": 1,
        "pages": 1
    }

    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json=orders_data,
        status=200
    )

    # "noa" should fuzzy match Noah Wolfe and Noah Whitnah
    orders = find_orders_by_name("noa")
    assert len(orders) >= 2
    customer_names = [o["shipTo"]["name"] for o in orders]
    assert any("Noah" in name for name in customer_names)


@responses.activate
def test_find_orders_by_name_prefers_exact_over_fuzzy():
    """Test that exact substring matches take precedence over fuzzy"""
    orders_data = {
        "orders": [
            {
                "orderId": 1,
                "orderNumber": "9001",
                "orderStatus": "awaiting_shipment",
                "shipTo": {"name": "Noah Wolfe"},
                "orderTotal": 100,
                "items": [],
                "tagIds": []
            },
            {
                "orderId": 2,
                "orderNumber": "9002",
                "orderStatus": "awaiting_shipment",
                "shipTo": {"name": "Nolan Cook"},
                "orderTotal": 200,
                "items": [],
                "tagIds": []
            }
        ],
        "total": 2,
        "page": 1,
        "pages": 1
    }

    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json=orders_data,
        status=200
    )

    # "Noah" should exact match only Noah Wolfe, not fuzzy match Nolan
    orders = find_orders_by_name("Noah")
    assert len(orders) == 1
    assert orders[0]["shipTo"]["name"] == "Noah Wolfe"
