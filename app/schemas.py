from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from .models import RequestStatus, DocumentType

class QuoteBase(BaseModel):
    partner_id: int
    price: float
    details: str

class QuoteCreate(QuoteBase):
    request_id: int

class Quote(QuoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int

class DocumentBase(BaseModel):
    doc_type: DocumentType
    file_path: str
    filename: str

class DocumentCreate(DocumentBase):
    request_id: int

class Document(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    uploaded_at: datetime

class RequestBase(BaseModel):
    description: str
    client_id: str

class RequestCreate(RequestBase):
    pass

class HistoricalRequestImport(RequestBase):
    status: Optional[RequestStatus] = RequestStatus.COMPLETED
    contract_expiration: Optional[date] = None
    adjustment_month: Optional[int] = None
    machine_id: Optional[str] = None

class RequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    contract_expiration: Optional[date] = None
    adjustment_month: Optional[int] = None
    machine_id: Optional[str] = None
    selected_quote_id: Optional[int] = None

class Request(RequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: RequestStatus
    created_at: datetime
    contract_expiration: Optional[date] = None
    adjustment_month: Optional[int] = None
    machine_id: Optional[str] = None
    selected_quote_id: Optional[int] = None
    quotes: List[Quote] = []
    documents: List[Document] = []

class PartnerBase(BaseModel):
    name: str
    contact_info: str

class PartnerCreate(PartnerBase):
    pass

class Partner(PartnerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
