from datetime import date
from decimal import Decimal

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from app.schemas import TotalSpent


@tool
def get_total_spent(date_from: date, date_to: date, config: RunnableConfig) -> dict:
    """Return the total amount spent between two dates (inclusive), in CHF.
    Use it for any question about how much was spent in a period.
    """
    company_id = config["configurable"]["company_id"]
    store = config["configurable"]["store"]
    receipts = store.list_receipts(company_id, date_from, date_to)
    total = sum((r.total for r in receipts), Decimal(0))

    result = TotalSpent(
        total=total, receipt_count=len(receipts), date_from=date_from, date_to=date_to
    )
    return result.model_dump_json()
