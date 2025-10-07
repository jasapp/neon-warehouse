"""
Pytest configuration and fixtures for neon-warehouse tests

Provides common fixtures for mocking ShipStation API responses.
"""

import pytest


@pytest.fixture
def sample_order():
    """Sample order response from ShipStation API"""
    return {
        "orderId": 1234567,
        "orderNumber": "9999",
        "orderKey": "test-key",
        "orderStatus": "awaiting_shipment",
        "customerEmail": "test@example.com",
        "orderDate": "2025-10-08T10:00:00.0000000",
        "shipDate": None,
        "shipTo": {
            "name": "Test Customer",
            "street1": "123 Test St",
            "city": "Testville",
            "state": "TS",
            "postalCode": "12345",
            "country": "US"
        },
        "orderTotal": 599.00,
        "items": [
            {
                "name": "Titanium DC2",
                "sku": "DC2-TI",
                "quantity": 1,
                "unitPrice": 559.00
            },
            {
                "name": "Battery Cover - 18650",
                "sku": "18650-cover",
                "quantity": 2,
                "unitPrice": 20.00
            }
        ],
        "tagIds": [],
        "shipments": []
    }


@pytest.fixture
def sample_order_with_tags():
    """Sample order with tags"""
    return {
        "orderId": 1234568,
        "orderNumber": "9998",
        "orderKey": "test-key-2",
        "orderStatus": "awaiting_shipment",
        "customerEmail": "tagged@example.com",
        "orderDate": "2025-10-08T10:00:00.0000000",
        "shipDate": None,
        "shipTo": {
            "name": "Tagged Customer"
        },
        "orderTotal": 559.00,
        "items": [
            {
                "name": "Titanium DC2",
                "sku": "DC2-TI",
                "quantity": 1,
                "unitPrice": 559.00
            }
        ],
        "tagIds": [
            {"tagId": 173102, "name": "RUSH"}
        ],
        "shipments": []
    }


@pytest.fixture
def sample_shipped_order():
    """Sample shipped order"""
    return {
        "orderId": 1234569,
        "orderNumber": "9997",
        "orderKey": "test-key-3",
        "orderStatus": "shipped",
        "customerEmail": "shipped@example.com",
        "orderDate": "2025-10-07T10:00:00.0000000",
        "shipDate": "2025-10-08T14:00:00.0000000",
        "shipTo": {
            "name": "Shipped Customer"
        },
        "orderTotal": 559.00,
        "items": [
            {
                "name": "Titanium DC2",
                "sku": "DC2-TI",
                "quantity": 1,
                "unitPrice": 559.00
            }
        ],
        "tagIds": [],
        "shipments": [
            {
                "trackingNumber": "1Z999AA10123456784",
                "carrierCode": "ups",
                "shipDate": "2025-10-08T14:00:00.0000000"
            }
        ]
    }


@pytest.fixture
def sample_orders_list(sample_order):
    """Sample list orders response"""
    return {
        "orders": [
            sample_order,
            {
                "orderId": 1234570,
                "orderNumber": "9996",
                "orderKey": "test-key-4",
                "orderStatus": "awaiting_shipment",
                "customerEmail": "customer2@example.com",
                "orderDate": "2025-10-08T11:00:00.0000000",
                "shipTo": {
                    "name": "Second Customer"
                },
                "orderTotal": 579.00,
                "items": [
                    {
                        "name": "Titanium DC2",
                        "sku": "DC2-TI",
                        "quantity": 1
                    }
                ],
                "tagIds": [],
                "shipments": []
            }
        ],
        "total": 2,
        "page": 1,
        "pages": 1
    }


@pytest.fixture
def sample_tags_list():
    """Sample tags list response"""
    return [
        {"tagId": 173102, "name": "RUSH"},
        {"tagId": 143376, "name": "DC0-Ti"},
        {"tagId": 143377, "name": "DC0-bronze"},
        {"tagId": 171102, "name": "Nov23 Drop"}
    ]
