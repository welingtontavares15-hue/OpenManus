from fastapi import FastAPI
from .routers import requests, partners, documents
from .database import engine
from . import models
from fastapi.staticfiles import StaticFiles
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dishwasher Workflow System",
    description="""
    API for managing the lifecycle of dishwasher procurement and maintenance.

    ## Workflow
    1. **Quotation**: Sales/Client initiates a request.
    2. **Supplier Interaction**: Partners submit quotes.
    3. **Selection**: A quote/partner is selected.
    4. **Contracting**: Contract is uploaded.
    5. **Installation**: Invoice (NF) is uploaded.
    6. **Technical Acceptance**: Final acceptance document is uploaded.
    7. **Completed**: Workflow finished.

    ## Features
    - Partner/Supplier management.
    - Document storage (Contracts, NFs, etc.) with security.
    - Contract expiration and adjustment notifications.
    - Historical data import.
    """,
    version="1.0.0"
)

app.include_router(requests.router, prefix="/api/requests", tags=["Requests"])
app.include_router(partners.router, prefix="/api/partners", tags=["Partners"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])

# Mount static files
app.mount("/dashboard", StaticFiles(directory="static", html=True), name="static")

@app.get("/", include_in_schema=False)
def read_root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")
