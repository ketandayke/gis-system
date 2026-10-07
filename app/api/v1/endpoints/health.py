from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health_check():
    """
    Check application health.
    """
    return {"status": "ok"}
