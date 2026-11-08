from datetime import date, timedelta


# Health check works without authentication
def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# A valid receipt is created and assigned to the caller's company
def test_create_receipt(client, muller_headers, valid_receipt):
    response = client.post("/v1/receipts", json=valid_receipt, headers=muller_headers)

    assert response.status_code == 201
    assert response.json()["company_id"] == "muller-ag"


# Without a token the request is rejected
def test_create_without_token(client, valid_receipt):
    response = client.post("/v1/receipts", json=valid_receipt)

    assert response.status_code == 401


# Net + VAT must match the total
def test_create_with_wrong_total(client, muller_headers, valid_receipt):
    receipt = {**valid_receipt, "total": "1.00"}

    response = client.post("/v1/receipts", json=receipt, headers=muller_headers)

    assert response.status_code == 422


# Only Swiss VAT rates are accepted
def test_create_with_wrong_vat_rate(client, muller_headers, valid_receipt):
    receipt = {**valid_receipt, "vat_rate": "15"}

    response = client.post("/v1/receipts", json=receipt, headers=muller_headers)

    assert response.status_code == 422


# A receipt cannot be dated in the future
def test_create_with_future_date(client, muller_headers, valid_receipt):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    receipt = {**valid_receipt, "receipt_date": tomorrow}

    response = client.post("/v1/receipts", json=receipt, headers=muller_headers)

    assert response.status_code == 422


# The client cannot set server-side fields like the company (mass assignment)
def test_create_with_extra_field(client, muller_headers, valid_receipt):
    receipt = {**valid_receipt, "company_id": "keller-gmbh"}

    response = client.post("/v1/receipts", json=receipt, headers=muller_headers)

    assert response.status_code == 422


# The list returns the company's receipts
def test_list_receipts(client, muller_headers, valid_receipt):
    client.post("/v1/receipts", json=valid_receipt, headers=muller_headers)

    response = client.get("/v1/receipts", headers=muller_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["company_id"] == "muller-ag"


# The date filter keeps only receipts inside the range
def test_list_filters_by_date(client, muller_headers, valid_receipt, bakery_receipt):
    client.post("/v1/receipts", json=valid_receipt, headers=muller_headers)  # 2026-10-15
    client.post("/v1/receipts", json=bakery_receipt, headers=muller_headers)  # 2026-10-22

    response = client.get(
        "/v1/receipts",
        params={"date_from": "2026-10-20", "date_to": "2026-10-31"},
        headers=muller_headers,
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["supplier_name"] == "Daily Bread Bakery"


# date_from after date_to is rejected
def test_list_with_inverted_dates(client, muller_headers):
    response = client.get(
        "/v1/receipts",
        params={"date_from": "2026-10-31", "date_to": "2026-10-01"},
        headers=muller_headers,
    )

    assert response.status_code == 422


# Tenant isolation: another company gets 404, not 403, so nothing leaks
def test_other_company_cannot_see_receipt(client, muller_headers, keller_headers, valid_receipt):
    receipt_id = client.post("/v1/receipts", json=valid_receipt, headers=muller_headers).json()["id"]

    response = client.get(f"/v1/receipts/{receipt_id}", headers=keller_headers)

    assert response.status_code == 404


# Tenant isolation: another company's list doesn't include it
def test_other_company_list_is_empty(client, muller_headers, keller_headers, valid_receipt):
    client.post("/v1/receipts", json=valid_receipt, headers=muller_headers)

    response = client.get("/v1/receipts", headers=keller_headers)

    assert response.json()["items"] == []


# Tenant isolation: another company cannot delete it, and the owner still has it
def test_other_company_cannot_delete_receipt(client, muller_headers, keller_headers, valid_receipt):
    receipt_id = client.post("/v1/receipts", json=valid_receipt, headers=muller_headers).json()["id"]

    response = client.delete(f"/v1/receipts/{receipt_id}", headers=keller_headers)

    assert response.status_code == 404
    assert client.get(f"/v1/receipts/{receipt_id}", headers=muller_headers).status_code == 200


# A deleted receipt is gone
def test_delete_then_get_returns_404(client, muller_headers, valid_receipt):
    receipt_id = client.post("/v1/receipts", json=valid_receipt, headers=muller_headers).json()["id"]

    delete_response = client.delete(f"/v1/receipts/{receipt_id}", headers=muller_headers)
    get_response = client.get(f"/v1/receipts/{receipt_id}", headers=muller_headers)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404