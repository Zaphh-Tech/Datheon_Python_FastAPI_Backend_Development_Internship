import logging

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, status
from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.core.config import settings
from app.core.rate_limit import RateLimiter

logger = logging.getLogger("datheon.notify")

router = APIRouter(prefix="/notify", tags=["Notify"])

rate_limited = RateLimiter()


class WebhookRequest(BaseModel):
    url: HttpUrl
    message: str = Field(..., max_length=2000)


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str = Field(..., max_length=200)
    body: str = Field(..., max_length=5000)


class Accepted(BaseModel):
    status: str = "accepted"
    detail: str


async def _dispatch_webhook(url: str, message: str) -> None:
    try:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, json={"message": message})
        logger.info("webhook %s -> %s", url, resp.status_code)
    except Exception as exc:
        logger.warning("webhook %s failed: %s", url, exc)


def _send_email(to: str, subject: str, body: str) -> None:
    logger.info("email to=%s subject=%r body=%r", to, subject, body)


@router.post(
    "/webhook",
    response_model=Accepted,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limited)],
)
async def send_webhook(payload: WebhookRequest, background: BackgroundTasks):
    background.add_task(_dispatch_webhook, str(payload.url), payload.message)
    return Accepted(detail=f"webhook to {payload.url} queued")


@router.post(
    "/email",
    response_model=Accepted,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limited)],
)
async def send_email(payload: EmailRequest, background: BackgroundTasks):
    background.add_task(_send_email, payload.to, payload.subject, payload.body)
    return Accepted(detail=f"email to {payload.to} queued")
