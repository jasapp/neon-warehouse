"""
Tests for mark_rush module
"""

import pytest
import responses
from tools.shipstation.mark_rush import (
    get_tag_id,
    order_has_tag,
    add_tag_to_order,
    find_order_by_number,
    find_orders_by_name
)


@responses.activate
def test_get_tag_id_success(sample_tags_list):
    """Test fetching tag ID by name"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json=sample_tags_list,
        status=200
    )

    tag_id = get_tag_id("RUSH")
    assert tag_id == 173102


@responses.activate
def test_get_tag_id_case_insensitive(sample_tags_list):
    """Test tag lookup is case-insensitive"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json=sample_tags_list,
        status=200
    )

    tag_id = get_tag_id("rush")
    assert tag_id == 173102

    tag_id = get_tag_id("RuSh")
    assert tag_id == 173102


@responses.activate
def test_get_tag_id_not_found(sample_tags_list):
    """Test when tag doesn't exist"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json=sample_tags_list,
        status=200
    )

    tag_id = get_tag_id("NONEXISTENT")
    assert tag_id is None


def test_order_has_tag_dict_format(sample_order_with_tags):
    """Test checking if order has tag (dict format)"""
    assert order_has_tag(sample_order_with_tags, 173102) is True
    assert order_has_tag(sample_order_with_tags, 999999) is False


def test_order_has_tag_int_list_format():
    """Test checking if order has tag (int list format)"""
    order = {
        "orderId": 123,
        "tagIds": [173102, 143376]
    }
    assert order_has_tag(order, 173102) is True
    assert order_has_tag(order, 999999) is False


def test_order_has_tag_none():
    """Test checking tags when tagIds is None"""
    order = {
        "orderId": 123,
        "tagIds": None
    }
    assert order_has_tag(order, 173102) is False


def test_order_has_tag_empty():
    """Test checking tags when tagIds is empty"""
    order = {
        "orderId": 123,
        "tagIds": []
    }
    assert order_has_tag(order, 173102) is False


@responses.activate
def test_add_tag_to_order_success():
    """Test adding tag to order"""
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/addtag",
        json={"success": True},
        status=200
    )

    result = add_tag_to_order(1234567, 173102)
    assert result is True

    # Verify request payload
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.body == b'{"orderId": 1234567, "tagId": 173102}'


@responses.activate
def test_add_tag_to_order_already_tagged(sample_order_with_tags):
    """Test adding tag when order already has it (idempotent)"""
    # Should not make API call if already tagged
    result = add_tag_to_order(1234568, 173102, order_data=sample_order_with_tags)
    assert result is True
    assert len(responses.calls) == 0  # No API call made


@responses.activate
def test_add_tag_to_order_api_error():
    """Test handling API error when adding tag"""
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/addtag",
        json={"error": "Server error"},
        status=500
    )

    result = add_tag_to_order(1234567, 173102)
    assert result is False


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
def test_find_orders_by_name_single_match(sample_order):
    """Test finding orders by customer name"""
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
    """Test finding orders by partial name match"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1, "page": 1, "pages": 1},
        status=200
    )

    # Should match "Test Customer" with partial search "Test"
    orders = find_orders_by_name("Test")
    assert len(orders) == 1
    assert orders[0]["orderNumber"] == "9999"


@responses.activate
def test_find_orders_by_name_case_insensitive(sample_order):
    """Test name search is case-insensitive"""
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
def test_find_orders_by_name_no_matches():
    """Test finding orders when no matches"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [], "total": 0, "page": 1, "pages": 1},
        status=200
    )

    orders = find_orders_by_name("Nonexistent Customer")
    assert orders == []


@responses.activate
def test_find_orders_by_name_multiple_matches(sample_orders_list):
    """Test finding multiple orders by name"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json=sample_orders_list,
        status=200
    )

    orders = find_orders_by_name("Customer")
    assert len(orders) == 2
    assert orders[0]["orderNumber"] == "9999"
    assert orders[1]["orderNumber"] == "9996"
