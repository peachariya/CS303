from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# นำเข้าระบบทำนายผล Machine Learning ที่เราทำไว้
from app.services.prediction_service import predict_sms_risk, predict_url_risk
from app.api import sms_router, url_router, graph_router, osint_router

app = FastAPI(
    title="Cybercrime Analyzer API",
    description="ระบบวิเคราะห์พฤติกรรมและเครือข่ายความเชื่อมโยงอาชญากรรมออนไลน์",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # รองรับหน้าเว็บ React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# กำหนดรูปแบบ Input/Output ให้ชัดเจนตามหัวข้อที่ 4
class SmsRequest(BaseModel):
    text: str

class UrlRequest(BaseModel):
    url: str

@app.post("/api/v1/check/sms", tags=["ML Prediction"])
def check_sms(request: SmsRequest):
    """
    Input: ข้อความ SMS
    Output: ระดับความเสี่ยง (0=ปลอดภัย, 1=น่าสงสัย, 2=หลอกลวงแน่นอน)
    """
    risk_level = predict_sms_risk(request.text)
    
    # แปลง Output ตาม 3 ระดับ
    status_mapping = {0: "Safe", 1: "Suspicious", 2: "Malicious"}
    
    return {
        "input_text": request.text,
        "risk_level": risk_level,
        "status": status_mapping.get(risk_level, "Safe"),
        "description": "วิเคราะห์จากความยาวข้อความ, การมีลิงก์แนบ, และจำนวนคำเสี่ยง"
    }

@app.post("/api/v1/check/url", tags=["ML Prediction"])
def check_url(request: UrlRequest):
    """
    Input: ลิงก์ URL
    Output: ระดับความเสี่ยง (0=ปลอดภัย, 1=น่าสงสัย, 2=ฟิชชิ่ง)
    """
    risk_level = predict_url_risk(request.url)
    
    status_mapping = {0: "Safe", 1: "Suspicious", 2: "Phishing"}
    
    return {
        "input_url": request.url,
        "risk_level": risk_level,
        "status": status_mapping.get(risk_level, "Safe"),
        "description": "วิเคราะห์จากความยาวลิงก์, จำนวนจุด/ขีดกลาง, และคำศัพท์อ่อนไหว"
    }

# Router เดิมของโปรเจกต์
app.include_router(sms_router.router, prefix="/api/sms", tags=["SMS Analysis"])
app.include_router(url_router.router, prefix="/api/url", tags=["URL Analysis"])
app.include_router(graph_router.router, prefix="/api/graph", tags=["Graph Analysis"])
app.include_router(osint_router.router, prefix="/api/osint", tags=["OSINT"])

@app.get("/")
def root():
    return {"message": "Cybercrime Analyzer API is running"}