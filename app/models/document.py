from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import datetime
import enum
from app.database import Base

class DocumentType(enum.Enum):
    CONTRACT = "contract"
    INVOICE = "invoice"  # NF
    ACCEPTANCE = "acceptance"
    OTHER = "other"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    doc_type = Column(Enum(DocumentType))
    file_path = Column(String)
    filename = Column(String)
    uploaded_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    request = relationship("Request", back_populates="documents")
