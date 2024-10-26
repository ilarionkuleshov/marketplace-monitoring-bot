from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def check_health() -> dict[str, str]:
    """Checks the health of the API."""
    return {"status": "ok"}
