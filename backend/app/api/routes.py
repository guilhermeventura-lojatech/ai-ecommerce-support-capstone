from fastapi import APIRouter, status

from backend.app.schemas import HealthResponse, SupportMessageRequest, SupportMessageResponse
from backend.app.services.router import SupportRouter

router = APIRouter()
support_router = SupportRouter()


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health() -> HealthResponse:
    return HealthResponse(status="ok", stage="foundation-backend")


@router.post(
    "/support/messages",
    response_model=SupportMessageResponse,
    status_code=status.HTTP_200_OK,
)
def process_support_message(request: SupportMessageRequest) -> SupportMessageResponse:
    return support_router.route(request)

