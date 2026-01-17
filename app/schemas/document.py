from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models import DocumentType

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
