from datetime import date
from decimal import Decimal

from app.agent.tools import get_total_spent
from app.schemas import Receipt
from app.store import ReceiptStore

store = ReceiptStore()
store.add_receipt(Receipt(
    supplier_name="CloudSoft AG", receipt_date=date(2026, 10, 15),
    net_amount=Decimal("50.00"), vat_rate=Decimal("8.1"), vat_amount=Decimal("4.05"),
    total=Decimal("54.05"), user_id="anna", company_id="muller-ag",
))
store.add_receipt(Receipt(
    supplier_name="Office Supplies Ltd", receipt_date=date(2026, 10, 20),
    net_amount=Decimal("100.00"), vat_rate=Decimal("8.1"), vat_amount=Decimal("8.10"),
    total=Decimal("108.10"), user_id="anna", company_id="muller-ag",
))
store.add_receipt(Receipt(
    supplier_name="Corner Shop", receipt_date=date(2026, 10, 18),
    net_amount=Decimal("10.00"), vat_rate=Decimal("8.1"), vat_amount=Decimal("0.81"),
    total=Decimal("10.81"), user_id="marco", company_id="keller-gmbh",
))

config = {"configurable": {"company_id": "muller-ag", "store": store}}
print(get_total_spent.invoke({"date_from": "2026-01-01", "date_to": "2026-11-01"}, config=config))
print(get_total_spent.args)