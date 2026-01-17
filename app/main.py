from fastapi import FastAPI
from app.api.v1.api import api_router
from app.core.config import settings
from app.database import engine
from app import models
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

app.include_router(api_router, prefix=settings.API_V1_STR)

# Keep old routes for compatibility or redirect them
app.include_router(api_router, prefix="/api")

# Mount static files
app.mount("/dashboard", StaticFiles(directory="static", html=True), name="static")

@app.get("/", include_in_schema=False)
def read_root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard")
