from sqlalchemy.orm import Session
from app import crud, models, schemas
from fastapi import HTTPException
import logging
import datetime

logger = logging.getLogger(__name__)

class WorkflowService:
    @staticmethod
    def select_quote(db: Session, request_id: int, quote_id: int):
        db_request = crud.get_request(db, request_id=request_id)
        if not db_request:
            raise HTTPException(status_code=404, detail="Request not found")

        # Verify quote exists and belongs to this request
        db_quote = db.query(models.Quote).filter(
            models.Quote.id == quote_id,
            models.Quote.request_id == request_id
        ).first()
        if not db_quote:
            raise HTTPException(status_code=404, detail="Quote not found for this request")

        logger.info(f"Request {request_id}: Selecting quote {quote_id}")
        return crud.update_request(db, request_id, schemas.RequestUpdate(
            status=models.RequestStatus.SELECTION,
            selected_quote_id=quote_id
        ))

    @staticmethod
    def handle_document_upload(db: Session, request_id: int, doc_type: models.DocumentType):
        db_request = crud.get_request(db, request_id=request_id)
        if not db_request:
            raise HTTPException(status_code=404, detail="Request not found")

        # Automatically advance status
        status_update = None
        if doc_type == models.DocumentType.CONTRACT:
            status_update = models.RequestStatus.CONTRACTING
        elif doc_type == models.DocumentType.INVOICE:
            status_update = models.RequestStatus.INSTALLATION
        elif doc_type == models.DocumentType.ACCEPTANCE:
            status_update = models.RequestStatus.TECHNICAL_ACCEPTANCE

        if status_update:
            crud.update_request(db, request_id, schemas.RequestUpdate(status=status_update))
            logger.info(f"Request {request_id} advanced to {status_update} via document upload")
            # Simulate integration notification
            logger.info(f"INTEGRATION: Notifying external system about status change for Request {request_id}")

    @staticmethod
    def complete_request(db: Session, request_id: int):
        db_request = crud.get_request(db, request_id=request_id)
        if not db_request:
            raise HTTPException(status_code=404, detail="Request not found")

        # If it's a new installation and we have machine data, update machine status
        if db_request.machine_id:
            db_machine = crud.get_machine(db, db_request.machine_id)
            if db_machine:
                db_machine.status = models.MachineStatus.ACTIVE
                db_machine.installation_date = datetime.date.today()
                db.commit()
                logger.info(f"Machine {db_machine.id} marked as ACTIVE upon request completion")

        return crud.update_request(db, request_id, schemas.RequestUpdate(status=models.RequestStatus.COMPLETED))
