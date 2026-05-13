# app/api/graph_router.py
from fastapi import APIRouter
from app.models.schemas import GraphAnalyzeRequest, GraphAnalyzeResponse
from app.services.graph_service import analyze_graph

router = APIRouter()

@router.post("/analyze", response_model=GraphAnalyzeResponse)
def analyze_graph_endpoint(request: GraphAnalyzeRequest):
    """วิเคราะห์เครือข่ายธุรกรรมเพื่อตรวจจับบัญชีม้า"""
    return analyze_graph(request.transactions)
