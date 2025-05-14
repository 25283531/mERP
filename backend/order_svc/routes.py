from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping():
    return {"msg": "order_svc pong"}