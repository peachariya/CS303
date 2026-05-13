# app/api/sms_router.py
from fastapi import APIRouter
from app.models.schemas import SMSAnalyzeRequest, SMSAnalyzeResponse
from app.services.sms_service import analyze_sms

router = APIRouter()

@router.post("/analyze", response_model=SMSAnalyzeResponse)
def analyze_sms_endpoint(request: SMSAnalyzeRequest):
    """วิเคราะห์ข้อความ SMS เพื่อตรวจจับการหลอกลวง"""
    return analyze_sms(request.text)
