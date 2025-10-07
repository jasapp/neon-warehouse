"""
Tests for list_tags module
"""

import pytest
import responses


@responses.activate
def test_list_tags_success(sample_tags_list):
    """Test listing tags successfully"""
    from tools.shipstation.list_tags import list_tags
    import sys
    from io import StringIO

    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json=sample_tags_list,
        status=200
    )

    # Capture stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        list_tags()
    finally:
        sys.stdout = sys.__stdout__

    output = captured_output.getvalue()

    # Verify output contains tag names
    assert "RUSH" in output
    assert "173102" in output


@responses.activate
def test_list_tags_sorted(sample_tags_list):
    """Test that tags are sorted alphabetically"""
    from tools.shipstation.list_tags import list_tags
    import sys
    from io import StringIO

    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json=sample_tags_list,
        status=200
    )

    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        list_tags()
    finally:
        sys.stdout = sys.__stdout__

    output = captured_output.getvalue()
    lines = [line.strip() for line in output.split('\n') if line.strip() and 'Available' not in line]

    # Extract tag names from output
    tag_names = []
    for line in lines:
        if '(ID:' in line:
            name = line.split('(ID:')[0].strip()
            tag_names.append(name)

    # Verify sorted order
    assert tag_names == sorted(tag_names)


@responses.activate
def test_list_tags_api_error():
    """Test handling API error"""
    from tools.shipstation.list_tags import list_tags

    responses.add(
        responses.GET,
        "https://ssapi.shipstation.com/accounts/listtags",
        json={"error": "Server error"},
        status=500
    )

    with pytest.raises(SystemExit):
        list_tags()
