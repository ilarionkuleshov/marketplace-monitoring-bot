from fastapi import APIRouter

router = APIRouter(prefix="/health")


@router.get("/")
async def check_health() -> dict[str, str]:
    """Checks the health of the API.

    Returns:
        dict[str, str]: A dictionary with the status of the API.

    """
    return {"status": "ok"}
