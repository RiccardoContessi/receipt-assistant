from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ReceiptCreate(BaseModel):
    """What the client sends when adding a receipt."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    
    supplier_name: str = Field(min_length=1, max_length=200)
    supplier_vat_number: str | None = Field(default=None, max_length=20, description="e.g. CHE-123.456.789")
    receipt_date: date
    currency: Literal["CHF"] = "CHF"
    net_amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    vat_rate: Decimal = Field(ge=0, max_digits=4, decimal_places=1, description="Percent: 0, 2.6, 3.8 or 8.1")
    vat_amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    total: Decimal = Field(ge=0, max_digits=12, decimal_places=2)

    # TODO: vat_rate in {0, 2.6, 3.8, 8.1}
    # TODO: receipt_date not in the future
    # TODO: net_amount + vat_amount == total (± 0.01)


class Receipt(ReceiptCreate):
    """A stored receipt: client fields plus server-set fields."""

    id: UUID = Field(default_factory=uuid4)
    user_id: str
    company_id: str
    account_number: str | None = None  # set later by classification
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))