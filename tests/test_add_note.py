"""
Tests for add_note module
"""

import pytest
import responses
from tools.shipstation.add_note import update_order_notes


@responses.activate
def test_update_order_notes_new_note(sample_order):
    """Test adding note to order with no existing notes"""
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/createorder",
        json={"success": True},
        status=200
    )

    order = sample_order.copy()
    order["internalNotes"] = ""

    result = update_order_notes(order, "test note")
    assert result is True

    # Verify request was made with updated notes
    assert len(responses.calls) == 1
    import json
    request_body = json.loads(responses.calls[0].request.body)
    assert request_body["internalNotes"] == "test note"


@responses.activate
def test_update_order_notes_append_to_existing(sample_order):
    """Test appending note to existing notes"""
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/createorder",
        json={"success": True},
        status=200
    )

    order = sample_order.copy()
    order["internalNotes"] = "existing note"

    result = update_order_notes(order, "new note")
    assert result is True

    # Verify notes were appended with comma separator
    import json
    request_body = json.loads(responses.calls[0].request.body)
    assert request_body["internalNotes"] == "existing note, new note"


@responses.activate
def test_update_order_notes_api_error(sample_order):
    """Test handling API error"""
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/createorder",
        json={"error": "Server error"},
        status=500
    )

    order = sample_order.copy()

    result = update_order_notes(order, "test note")
    assert result is False


@responses.activate
def test_update_order_notes_preserves_order_data(sample_order):
    """Test that full order data is sent to API"""
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/createorder",
        json={"success": True},
        status=200
    )

    order = sample_order.copy()
    order["internalNotes"] = ""

    update_order_notes(order, "test")

    # Verify full order structure was sent
    import json
    request_body = json.loads(responses.calls[0].request.body)
    assert request_body["orderId"] == sample_order["orderId"]
    assert request_body["orderNumber"] == sample_order["orderNumber"]
    assert request_body["orderStatus"] == sample_order["orderStatus"]
    assert "items" in request_body
