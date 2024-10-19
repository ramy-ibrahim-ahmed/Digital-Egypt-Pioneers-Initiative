from fastapi import APIRouter, HTTPException, Cookie, Request
from pydantic import BaseModel
from typing import Optional
from ..controllers.ChainController import ChainController
from ..models import StudentModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class Query(BaseModel):
    student_query: str

@router.post("/chat")
async def chat(
    request: Request, query: Query, validated_username: Optional[str] = Cookie(None)
):
    """
    Use the validated username stored in the cookie to process the RAG query.
    """
    if not validated_username:
        raise HTTPException(status_code=400, detail="Unauthorized User")

    chain_controller = ChainController()
    student_model = StudentModel(db_client=request.app.db_client)

    transcript = await student_model.get_transcript_by_username(
        username=validated_username
    )
    chain_controller.set_transcript(transcript=transcript)

    response = chain_controller.process(query=query.student_query)

    return {"username": validated_username, "response": response}
