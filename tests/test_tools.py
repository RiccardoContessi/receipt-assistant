from datetime import date
from decimal import Decimal

from app.agent.tools import get_total_spent
from app.schemas import Receipt
from app.store import ReceiptStore


def make_receipt(total: str, day: date, company_id: str) -> Receipt:
    net = Decimal(total) / Decimal("1.081")
    vat = Decimal(total) - net.quantize(Decimal("0.01"))
    return Receipt(
        supplier_name="Test Supplier",
        receipt_date=day,
        net_amount=net.quantize(Decimal("0.01")),
        vat_rate=Decimal("8.1"),
        vat_amount=vat,
        total=Decimal(total),
        user_id="test",
        company_id=company_id,
    )


# The tool sums only the caller's company receipts inside the period
def test_total_spent_is_scoped_to_company_and_period():
    store = ReceiptStore()
    store.add_receipt(make_receipt("54.05", date(2026, 10, 15), "muller-ag"))
    store.add_receipt(make_receipt("108.10", date(2026, 10, 20), "muller-ag"))
    store.add_receipt(
        make_receipt("200.00", date(2026, 9, 10), "muller-ag")
    )  # outside the period
    store.add_receipt(
        make_receipt("10.81", date(2026, 10, 18), "keller-gmbh")
    )  # other company

    config = {"configurable": {"company_id": "muller-ag", "store": store}}
    result = get_total_spent.invoke(
        {"date_from": "2026-10-01", "date_to": "2026-10-31"}, config=config
    )

    assert '"total":"162.15"' in result
    assert '"receipt_count":2' in result


# The model must never see the company or the config among the tool arguments
def test_tool_hides_config_from_the_model():
    assert set(get_total_spent.args) == {"date_from", "date_to"}
