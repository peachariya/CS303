# app/api/osint_router.py
from fastapi import APIRouter
from app.models.schemas import OSINTRequest, OSINTResponse
from app.services.osint_service import run_osint

router = APIRouter()

@router.post("/lookup", response_model=OSINTResponse)
async def osint_lookup(request: OSINTRequest):
    """สืบค้นข้อมูล OSINT จาก VirusTotal และ WHOIS"""
    return await run_osint(request.target)
