from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ALLOWED_VAT_RATES = {Decimal(0), Decimal("2.6"), Decimal("3.8"), Decimal("8.1")}


class ReceiptCreate(BaseModel):
    """What the client sends when adding a receipt."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    supplier_name: str = Field(min_length=1, max_length=200)
    supplier_vat_number: str | None = Field(
        default=None, max_length=20, description="e.g. CHE-123.456.789"
    )
    receipt_date: date
    currency: Literal["CHF"] = "CHF"
    net_amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    vat_rate: Decimal = Field(
        ge=0, max_digits=4, decimal_places=1, description="Percent: 0, 2.6, 3.8 or 8.1"
    )
    vat_amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    total: Decimal = Field(ge=0, max_digits=12, decimal_places=2)

    # validators
    @field_validator("receipt_date")
    @classmethod
    def check_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError(f"receipt date {value} is in the future")
        return value

    @field_validator("vat_rate")
    @classmethod
    def check_vat_rate(cls, value: Decimal) -> Decimal:
        if value not in ALLOWED_VAT_RATES:
            raise ValueError(f"vat_rate {value} is not allowed: use 0, 2.6, 3.8 or 8.1")
        return value

    @model_validator(mode="after")
    def check_amount(self) -> Self:
        if self.net_amount + self.vat_amount >= self.total * Decimal(
            "0.99"
        ) and self.net_amount + self.vat_amount <= self.total * Decimal("1.01"):
            return self
        raise ValueError(
            f"total {self.total} doesn't match net {self.net_amount} + VAT {self.vat_amount}"
        )


class Receipt(ReceiptCreate):
    """A stored receipt: client fields plus server-set fields."""

    id: UUID = Field(default_factory=uuid4)
    user_id: str
    company_id: str
    account_number: str | None = None  # set later by classification
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReceiptList(BaseModel):
    """a list of receipts"""

    items: list[Receipt]


class ReceiptFilter(BaseModel):
    """filter parameters for receipts, not mandatory"""

    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def check_date(self) -> Self:
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError(
                f"date_from {self.date_from} is after date_to {self.date_to}"
            )
        return self


class ChatRequest(BaseModel):
    """user request"""

    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=2, max_length=2000)
    thread_id: str | None = None


class ChatResponse(BaseModel):
    """system response"""

    answer: str
    thread_id: str


class CurrentUser(BaseModel):
    user_id: str
    company_id: str


class TotalSpent(BaseModel):
    total: Decimal
    currency: Literal["CHF"] = "CHF"
    receipt_count: int
    date_from: date
    date_to: date
