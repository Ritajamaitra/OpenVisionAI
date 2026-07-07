from fastapi import APIRouter # type: ignore

router = APIRouter()

@router.get("/health")
def health():

    return {
        "status":"healthy",
        "version":"0.1.0",
        "service":"OpenVisionAI"
    }