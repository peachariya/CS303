from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# นำเข้าระบบทำนายผล Machine Learning ที่เราเพิ่งสร้าง
from app.services.prediction_service import predict_sms_risk, predict_url_risk
from app.api import sms_router, url_router, graph_router, osint_router

app = FastAPI(
    title="Cybercrime Analyzer API",
    description="ระบบวิเคราะห์พฤติกรรมและเครือข่ายความเชื่อมโยงอาชญากรรมออนไลน์",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:5173"
    ], # เพิ่มพอร์ต 3001 ของหน้าเว็บที่คุณอริยารันอยู่
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint สำหรับรับข้อมูลจาก Frontend มาเช็กกับ ML Model ---
class TextRequest(BaseModel):
    text: str

class UrlRequest(BaseModel):
    url: str

@app.post("/api/v1/check/sms")
def check_sms(request: TextRequest):
    risk_level = predict_sms_risk(request.text)
    return {
        "risk_level": risk_level,
        "status": "Malicious" if risk_level == 2 else "Safe",
        "description": "ระบบวิเคราะห์จากความยาวข้อความ, การตรวจพบลิงก์แนบ, และการนับจำนวนคำศัพท์กลุ่มเสี่ยง"
    }

@app.post("/api/v1/check/url")
def check_url(request: UrlRequest):
    risk_level = predict_url_risk(request.url)
    return {
        "risk_level": risk_level,
        "status": "Phishing" if risk_level > 0 else "Safe",
        "description": "ระบบวิเคราะห์จากความยาวลิงก์, จำนวนจุด/ขีดกลาง, และการตรวจจับคำสำคัญที่อ่อนไหว"
    }
# --------------------------------------------------------------------------

app.include_router(sms_router.router, prefix="/api/sms", tags=["SMS Analysis"])
app.include_router(url_router.router, prefix="/api/url", tags=["URL Analysis"])
app.include_router(graph_router.router, prefix="/api/graph", tags=["Graph Analysis"])
app.include_router(osint_router.router, prefix="/api/osint", tags=["OSINT"])

@app.get("/")
def root():
    return {"message": "Cybercrime Analyzer API is running"}