from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import sms_router, url_router, graph_router, osint_router

app = FastAPI(
    title="Cybercrime Analyzer API",
    description="ระบบวิเคราะห์พฤติกรรมและเครือข่ายความเชื่อมโยงอาชญากรรมออนไลน์",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sms_router.router, prefix="/api/sms", tags=["SMS Analysis"])
app.include_router(url_router.router, prefix="/api/url", tags=["URL Analysis"])
app.include_router(graph_router.router, prefix="/api/graph", tags=["Graph Analysis"])
app.include_router(osint_router.router, prefix="/api/osint", tags=["OSINT"])

@app.get("/")
def root():
    return {"message": "Cybercrime Analyzer API is running"}
