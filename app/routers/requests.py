from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..database import get_db
import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=schemas.Request, summary="Create a new request")
def create_request(request: schemas.RequestCreate, db: Session = Depends(get_db)):
    """Initiates a new dishwasher procurement workflow."""
    db_request = crud.create_request(db=db, request=request)
    logger.info(f"Created new request ID {db_request.id} for client {db_request.client_id}")
    return db_request

@router.get("/", response_model=List[schemas.Request], summary="List all requests")
def read_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_requests(db, skip=skip, limit=limit)

@router.get("/{request_id}", response_model=schemas.Request, summary="Get request details")
def read_request(request_id: int, db: Session = Depends(get_db)):
    db_request = crud.get_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return db_request

@router.put("/{request_id}/status", response_model=schemas.Request, summary="Update request status")
def update_request_status(request_id: int, status: models.RequestStatus, db: Session = Depends(get_db)):
    """Manually update the status of a request."""
    request_update = schemas.RequestUpdate(status=status)
    return crud.update_request(db=db, request_id=request_id, request_update=request_update)

@router.post("/{request_id}/quotes", response_model=schemas.Quote, summary="Submit a quote")
def submit_quote(request_id: int, quote: schemas.QuoteBase, db: Session = Depends(get_db)):
    """Partners can submit quotes for a specific request."""
    # Check if request exists
    db_request = crud.get_request(db, request_id=request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Check if request is in correct status
    if db_request.status != models.RequestStatus.QUOTATION and db_request.status != models.RequestStatus.SUPPLIER_INTERACTION:
         raise HTTPException(status_code=400, detail="Cannot submit quotes at this stage")

    # Update status to supplier interaction if it was quotation
    if db_request.status == models.RequestStatus.QUOTATION:
        crud.update_request(db, request_id, schemas.RequestUpdate(status=models.RequestStatus.SUPPLIER_INTERACTION))

    quote_create = schemas.QuoteCreate(**quote.model_dump(), request_id=request_id)
    return crud.create_quote(db=db, quote=quote_create)

@router.post("/{request_id}/select-quote", response_model=schemas.Request, summary="Select a quote")
def select_quote(request_id: int, quote_id: int, db: Session = Depends(get_db)):
    """Select a specific quote from a partner to move forward."""
    db_request = crud.get_request(db, request_id=request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Verify quote exists and belongs to this request
    db_quote = db.query(models.Quote).filter(models.Quote.id == quote_id, models.Quote.request_id == request_id).first()
    if not db_quote:
        raise HTTPException(status_code=404, detail="Quote not found for this request")

    logger.info(f"Request {request_id}: Selecting quote {quote_id} from partner {db_quote.partner_id}")
    return crud.update_request(db, request_id, schemas.RequestUpdate(
        status=models.RequestStatus.SELECTION,
        selected_quote_id=quote_id
    ))

@router.post("/{request_id}/complete-technical-acceptance", response_model=schemas.Request, summary="Complete technical acceptance")
def complete_technical_acceptance(request_id: int, db: Session = Depends(get_db)):
    """Marks the technical acceptance stage as complete."""
    db_request = crud.get_request(db, request_id=request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    return crud.update_request(db, request_id, schemas.RequestUpdate(status=models.RequestStatus.COMPLETED))

@router.get("/notifications/upcoming", response_model=List[schemas.Request], summary="Get upcoming notifications")
def get_upcoming_notifications(db: Session = Depends(get_db)):
    """Returns requests with contracts expiring or due for adjustment in the next 30 days."""
    today = datetime.date.today()
    next_month = today + datetime.timedelta(days=30)

    # Contracts expiring in the next 30 days
    expiring = db.query(models.Request).filter(
        models.Request.contract_expiration >= today,
        models.Request.contract_expiration <= next_month
    ).all()

    # Contracts with adjustment month being the current or next month
    current_month = today.month
    next_month_num = (today.month % 12) + 1

    adjusting = db.query(models.Request).filter(
        models.Request.adjustment_month.in_([current_month, next_month_num])
    ).all()

    # Combine and remove duplicates
    notifications = list(set(expiring + adjusting))
    return notifications

@router.put("/{request_id}/contract-details", response_model=schemas.Request, summary="Update contract details")
def update_contract_details(request_id: int, update: schemas.RequestUpdate, db: Session = Depends(get_db)):
    """Updates contract-specific fields like expiration date and adjustment month."""
    return crud.update_request(db, request_id, update)

@router.post("/import-history", response_model=List[schemas.Request], summary="Import historical data")
def import_history(historical_requests: List[schemas.HistoricalRequestImport], db: Session = Depends(get_db)):
    """Bulk imports historical machine data for the FY2026 goal."""
    imported = []
    for req_data in historical_requests:
        # Create request with all provided data
        db_req = models.Request(**req_data.model_dump())
        db.add(db_req)
        db.commit()
        db.refresh(db_req)
        imported.append(db_req)
    return imported
