from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.prediction_service import predict_sms_risk, predict_url_risk

app = FastAPI()

# เปิดให้ Frontend (React) สามารถยิง API ข้าม Origin กันได้ (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือระบุ URL ของเว็บ เช่น ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

class UrlRequest(BaseModel):
    url: str

@app.post("/api/v1/check/sms")
def check_sms(request: TextRequest):
    risk_level = predict_sms_risk(request.text)
    return {
        "risk_level": risk_level,
        "status": "Malicious" if risk_level == 2 else "Safe"
    }

@app.post("/api/v1/check/url")
def check_url(request: UrlRequest):
    risk_level = predict_url_risk(request.url)
    return {
        "risk_level": risk_level,
        "status": "Phishing" if risk_level > 0 else "Safe"
    }