# app/api/url_router.py
from fastapi import APIRouter
from app.models.schemas import URLAnalyzeRequest, URLAnalyzeResponse
from app.services.url_service import analyze_url

router = APIRouter()

@router.post("/analyze", response_model=URLAnalyzeResponse)
def analyze_url_endpoint(request: URLAnalyzeRequest):
    """วิเคราะห์ URL เพื่อตรวจจับ Phishing"""
    return analyze_url(request.url)
