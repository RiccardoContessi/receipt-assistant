import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import ReceiptStore, get_store


@pytest.fixture
def client():
    store = ReceiptStore()  # fresh, empty store for each test
    app.dependency_overrides[get_store] = lambda: store # override of get_store for tests

    with TestClient(app) as test_client:
        yield test_client  # the test runs here

    app.dependency_overrides.clear()  # after the test executions, restore the real dependencies


@pytest.fixture
def muller_headers():
    # Auth header of a logged-in user, as a real client would send it
    return {"Authorization": "Bearer token-muller"}

@pytest.fixture
def keller_headers():
    return {"Authorization": "Bearer token-keller"}


@pytest.fixture
def valid_receipt():
    return {
        "supplier_name": "CloudSoft AG",
        "supplier_vat_number": "CHE-123.456.789 MWST",
        "receipt_date": "2026-10-15",
        "currency": "CHF",
        "net_amount": "50.00",
        "vat_rate": "8.1",
        "vat_amount": "4.05",
        "total": "54.05",
    }


@pytest.fixture
def wrong_receipt_total():
    return {
        "supplier_name": "CloudSoft AG",
        "supplier_vat_number": "CHE-123.456.789 MWST",
        "receipt_date": "2026-10-15",
        "currency": "CHF",
        "net_amount": "10.00",
        "vat_rate": "8.1",
        "vat_amount": "4.05",
        "total": "54.05",
    }


@pytest.fixture
def wrong_receipt_vat_rate():
    return {
        "supplier_name": "CloudSoft AG",
        "supplier_vat_number": "CHE-123.456.789 MWST",
        "receipt_date": "2026-10-15",
        "currency": "CHF",
        "net_amount": "50.00",
        "vat_rate": "15",
        "vat_amount": "4.05",
        "total": "54.05",
    }

@pytest.fixture
def bakery_receipt():
    return {
        "supplier_name": "Daily Bread Bakery",
        "supplier_vat_number": None,
        "receipt_date": "2026-10-22",
        "currency": "CHF",
        "net_amount": "30.00",
        "vat_rate": "2.6",
        "vat_amount": "0.78",
        "total": "30.78",
    }