"""
Visual QA router – ask questions about uploaded images.

All endpoints are prefixed with ``/api/v1`` and tagged ``visual-qa``.
"""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from src.api.dependencies import get_optional_user
from src.models.api_schemas import VisualQAResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["visual-qa"])

_VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}


@router.post("/visual-qa", response_model=VisualQAResponse)
async def visual_qa(
    image: UploadFile = File(...),
    question: str = Form(...),
    context: Optional[str] = Form(None),
    current_user=Depends(get_optional_user),
) -> VisualQAResponse:
    """Upload an image and ask a natural-language question about it.

    Uses the Gemini Vision–powered Visual QA system when available,
    otherwise returns a graceful fallback.
    """
    # ── Validate image ──
    _validate_image(image)

    # ── Save upload ──
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{uuid.uuid4()}_{image.filename}"
    content = await image.read()
    file_path.write_bytes(content)

    # ── Run VQA ──
    try:
        from src.ai_models.visual_qa_system import get_vqa_system

        vqa = get_vqa_system()
        result = vqa.answer_question_about_image(
            image_path=str(file_path),
            question=question,
            context=context,
        )
        return VisualQAResponse(**result)

    except ImportError:
        logger.warning("VQA system not available — returning fallback")
    except Exception as exc:
        logger.error("VQA error: %s", exc)

    # ── Fallback ──
    from datetime import datetime

    return VisualQAResponse(
        id=f"vqa_fallback_{int(datetime.now().timestamp())}",
        question=question,
        answer=(
            "The Visual QA system is currently unavailable. "
            "Please ensure the Gemini API key is configured and try again."
        ),
        confidence=0.0,
        timestamp=datetime.now().isoformat(),
        image_path=str(file_path),
        processing_method="Fallback Response",
    )


def _validate_image(image: UploadFile) -> None:
    is_image_mime = image.content_type and image.content_type.startswith("image/")
    has_valid_ext = (
        image.filename and Path(image.filename).suffix.lower() in _VALID_IMAGE_EXTENSIONS
    )
    if not (is_image_mime or has_valid_ext):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (jpg, jpeg, png, gif, bmp, webp)",
        )
