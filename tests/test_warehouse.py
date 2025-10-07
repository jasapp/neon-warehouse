"""
Tests for warehouse unified command
"""

import pytest
import responses
from tools.shipstation.warehouse import warehouse_command


@responses.activate
def test_warehouse_command_rush_detection(sample_order):
    """Test that RUSH is detected and routed correctly"""
    # Mock tag list
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json=[{"tagId": 173102, "name": "RUSH"}],
        status=200
    )

    # Mock order fetch
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1},
        status=200
    )

    # Mock add tag
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/addtag",
        json={"success": True},
        status=200
    )

    # Should route to mark_rush
    warehouse_command("9999", "RUSH", confirm=False)

    # Verify add tag was called
    tag_calls = [c for c in responses.calls if "addtag" in c.request.url]
    assert len(tag_calls) == 1


@responses.activate
def test_warehouse_command_rush_case_insensitive(sample_order):
    """Test that RUSH detection is case-insensitive"""
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json=[{"tagId": 173102, "name": "RUSH"}],
        status=200
    )

    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1},
        status=200
    )

    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/addtag",
        json={"success": True},
        status=200
    )

    # lowercase "rush" should still work
    warehouse_command("9999", "rush", confirm=False)

    tag_calls = [c for c in responses.calls if "addtag" in c.request.url]
    assert len(tag_calls) == 1


@responses.activate
def test_warehouse_command_note_detection(sample_order):
    """Test that non-RUSH text routes to add_note"""
    # Mock tag lists
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json=[
            {"tagId": 173102, "name": "RUSH"},
            {"tagId": 167720, "name": "Special NOTE!"}
        ],
        status=200
    )

    # Mock order fetch
    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/orders",
        json={"orders": [sample_order], "total": 1},
        status=200
    )

    # Mock add tag (Special NOTE!)
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/addtag",
        json={"success": True},
        status=200
    )

    # Mock update order notes
    responses.add(
        responses.POST,
        "https://ssapi.shipstation.com/orders/createorder",
        json={"success": True},
        status=200
    )

    # Should route to add_note
    warehouse_command("9999", "no memory", confirm=False)

    # Verify createorder was called (for notes)
    note_calls = [c for c in responses.calls if "createorder" in c.request.url]
    assert len(note_calls) == 1

    # Verify note content
    import json
    request_body = json.loads(note_calls[0].request.body)
    assert "no memory" in request_body["internalNotes"]
