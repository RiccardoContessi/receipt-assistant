from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, Query, status

from app.deps import get_current_user
from app.schemas import CurrentUser, Receipt, ReceiptCreate, ReceiptFilter, ReceiptList
from app.store import ReceiptStore, get_store

# authenticated user, resolved from the bearer token
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
# shared receipt store, injected per request
StoreDep = Annotated[ReceiptStore, Depends(get_store)]


app = FastAPI(title="Receipt Assistant")
receipts = APIRouter(prefix="/v1/receipts", tags=["receipts"])


@app.get("/health")
def health():
    return {"status": "ok"}


@receipts.post("", status_code=status.HTTP_201_CREATED)
def post_receipts(
    payload: ReceiptCreate, store: StoreDep, user: CurrentUserDep
) -> Receipt:
    receipt = Receipt(
        **payload.model_dump(), user_id=user.user_id, company_id=user.company_id
    )
    return store.add_receipt(receipt)


@receipts.get("", status_code=status.HTTP_200_OK)
def get_receipts(
    filters: Annotated[ReceiptFilter, Query()], user: CurrentUserDep, store: StoreDep
) -> ReceiptList:

    receipts_list = store.list_receipts(
        user.company_id, filters.date_from, filters.date_to
    )
    return ReceiptList(items=receipts_list)


@receipts.get("/{receipt_id}", status_code=status.HTTP_200_OK)
def get_receipt(
    receipt_id: Annotated[UUID, Path()], user: CurrentUserDep, store: StoreDep
) -> Receipt:
    receipt = store.get_receipt(user.company_id, receipt_id)
    if receipt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found"
        )
    return receipt


@receipts.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(
    receipt_id: Annotated[UUID, Path()], user: CurrentUserDep, store: StoreDep
):
    if not store.delete_receipt(user.company_id, receipt_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found"
        )


app.include_router(receipts)
