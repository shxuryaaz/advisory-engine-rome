from fastapi import APIRouter, HTTPException

from models.schemas import FeedbackRequest, FeedbackResponse
from services.user_model import user_model_service

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(payload: FeedbackRequest) -> FeedbackResponse:
    try:
        return await user_model_service.update_user_model(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
