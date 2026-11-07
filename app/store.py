from datetime import date
from uuid import UUID

from app.schemas import Receipt


class ReceiptStore:
    def __init__(self):
        self._receipts: dict[UUID, Receipt] = {}

    def add_receipt(self, receipt: Receipt) -> Receipt:
        self._receipts[receipt.id] = receipt
        return self._receipts[receipt.id]

    def get_receipt(self, company_id: str, receipt_id: UUID) -> Receipt | None:
        receipt = self._receipts.get(receipt_id)
        if receipt is None or receipt.company_id != company_id:
            return None
        return receipt

    def delete_receipt(self, company_id: str, receipt_id: UUID) -> bool:
        if self.get_receipt(company_id, receipt_id) is None:
            return False
        del self._receipts[receipt_id]
        return True

    def list_receipts(
        self,
        company_id: str,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Receipt]:
        receipts = [
            r
            for r in self._receipts.values()
            if r.company_id == company_id
            and (date_from is None or r.receipt_date >= date_from)
            and (date_to is None or r.receipt_date <= date_to)
        ]
        return sorted(receipts, key=lambda r: r.receipt_date)


_store = ReceiptStore()


def get_store() -> ReceiptStore:
    return _store
