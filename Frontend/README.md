# 🛡️ Cybercrime Network Analyzer

ระบบวิเคราะห์พฤติกรรมและเครือข่ายความเชื่อมโยงอาชญากรรมออนไลน์ด้วยการเรียนรู้ของเครื่อง  
โดย นางสาวอริยา ตั้งโรจนกุล — วิทยาการคอมพิวเตอร์ มหาวิทยาลัยธรรมศาสตร์

---

## 📁 โครงสร้างโปรเจกต์

```
cybercrime-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/
│   │   │   ├── sms_router.py    # POST /api/sms/analyze
│   │   │   ├── url_router.py    # POST /api/url/analyze
│   │   │   ├── graph_router.py  # POST /api/graph/analyze
│   │   │   └── osint_router.py  # POST /api/osint/lookup
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   └── services/
│   │       ├── sms_service.py   # NLP วิเคราะห์ SMS ภาษาไทย
│   │       ├── url_service.py   # ตรวจจับ Phishing URL
│   │       ├── graph_service.py # NetworkX วิเคราะห์บัญชีม้า
│   │       └── osint_service.py # VirusTotal + WHOIS
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── SMSAnalyzer.jsx    # หน้าวิเคราะห์ SMS
    │   │   ├── URLAnalyzer.jsx    # หน้าวิเคราะห์ URL
    │   │   ├── GraphAnalyzer.jsx  # กราฟเครือข่ายบัญชีม้า
    │   │   ├── OSINTLookup.jsx    # OSINT ค้นหาข้อมูล
    │   │   └── RiskBadge.jsx      # Component ระดับความเสี่ยง
    │   └── services/
    │       └── api.js             # HTTP client
    └── package.json
```

---

## 🚀 วิธีติดตั้งและรันระบบ

### 1. Backend

```bash
cd backend

# สร้าง virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
# หรือ: venv\Scripts\activate    # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# ตั้งค่า API Key (VirusTotal)
cp .env.example .env
# แก้ไข .env ใส่ VIRUSTOTAL_API_KEY ของคุณ

# รัน server
uvicorn app.main:app --reload --port 8000
```

Backend API จะทำงานที่ http://localhost:8000  
Swagger docs: http://localhost:8000/docs

---

### 2. Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend จะทำงานที่ http://localhost:3000

---

## 🔌 API Endpoints

| Method | Path                | คำอธิบาย                        |
|--------|---------------------|----------------------------------|
| POST   | /api/sms/analyze    | วิเคราะห์ SMS หลอกลวง           |
| POST   | /api/url/analyze    | ตรวจจับ Phishing URL             |
| POST   | /api/graph/analyze  | วิเคราะห์เครือข่ายบัญชีม้า     |
| POST   | /api/osint/lookup   | VirusTotal + WHOIS lookup        |

### ตัวอย่าง Request

```json
// POST /api/sms/analyze
{ "text": "ด่วน! บัญชีถูกระงับ คลิก http://kbank-verify.xyz" }

// POST /api/url/analyze
{ "url": "http://kbank-secure.xyz/login" }

// POST /api/graph/analyze
{
  "transactions": [
    { "from_account": "A001", "to_account": "HUB", "amount": 50000, "timestamp": "2024-01-15T09:00:00" },
    { "from_account": "A002", "to_account": "HUB", "amount": 35000, "timestamp": "2024-01-15T09:15:00" }
  ]
}

// POST /api/osint/lookup
{ "target": "https://suspicious-site.xyz" }
```

---

## 🧠 เทคโนโลยีที่ใช้

| ส่วน        | เทคโนโลยี                                      |
|-------------|------------------------------------------------|
| Backend     | Python 3.11, FastAPI, Uvicorn                  |
| NLP         | PyThaiNLP, scikit-learn (TF-IDF + LogReg)      |
| Graph       | NetworkX (Directed Graph + Hub Detection)      |
| OSINT       | VirusTotal API v3, python-whois                |
| Frontend    | React 18, Vite, Tailwind CSS                   |
| Visualization | SVG Force-Directed Graph (custom)            |

---

## ⚙️ Environment Variables

```env
VIRUSTOTAL_API_KEY=your_key_here   # จาก https://www.virustotal.com/gui/my-apikey
```
