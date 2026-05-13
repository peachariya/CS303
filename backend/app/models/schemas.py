from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# --- SMS Models ---
class SMSAnalyzeRequest(BaseModel):
    text: str

class SMSAnalyzeResponse(BaseModel):
    text: str
    risk_score: float          # 0.0 - 1.0
    risk_level: RiskLevel
    detected_patterns: List[str]
    suspicious_keywords: List[str]
    explanation: str

# --- URL Models ---
class URLAnalyzeRequest(BaseModel):
    url: str

class URLAnalyzeResponse(BaseModel):
    url: str
    risk_score: float
    risk_level: RiskLevel
    is_phishing: bool
    domain_age_days: Optional[int]
    explanation: str

# --- Graph / Money Mule Models ---
class Transaction(BaseModel):
    from_account: str
    to_account: str
    amount: float
    timestamp: str             # ISO format string

class GraphAnalyzeRequest(BaseModel):
    transactions: List[Transaction]

class NodeInfo(BaseModel):
    id: str
    risk_score: float
    total_received: float
    total_sent: float
    transaction_count: int
    is_hub: bool               # บัญชีม้าตัวกลาง

class EdgeInfo(BaseModel):
    source: str
    target: str
    amount: float
    timestamp: str

class GraphAnalyzeResponse(BaseModel):
    nodes: List[NodeInfo]
    edges: List[EdgeInfo]
    suspected_mule_accounts: List[str]
    hub_accounts: List[str]

# --- OSINT Models ---
class OSINTRequest(BaseModel):
    target: str                # URL or IP or domain

class OSINTResponse(BaseModel):
    target: str
    virustotal: Optional[dict]
    whois: Optional[dict]
    summary: str
