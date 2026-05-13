"""
บริการวิเคราะห์ URL เพื่อตรวจจับเว็บไซต์ตกเบ็ด (Phishing)
ใช้การสกัด Feature จาก URL + Rule-based + ML classifier
"""

import re
from urllib.parse import urlparse
from typing import Optional
from app.models.schemas import RiskLevel

# -------------------------------------------------------
# Feature extraction จาก URL
# -------------------------------------------------------

SUSPICIOUS_TLD = {".xyz", ".top", ".club", ".work", ".site", ".online",
                  ".bid", ".win", ".loan", ".click", ".link"}

LEGIT_THAI_DOMAINS = {
    "kasikornbank.com", "kbank.co.th", "scb.co.th",
    "bangkokbank.com", "ktb.co.th", "krungsri.com",
    "bbl.co.th", "gov.th", "moph.go.th", "mof.go.th",
    "revenue.go.th", "rd.go.th", "bam.co.th", "truemoney.com",
}

def extract_url_features(url: str) -> dict:
    """สกัด features จาก URL สำหรับการวิเคราะห์"""
    try:
        parsed = urlparse(url if url.startswith("http") else "http://" + url)
    except Exception:
        return {}

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    full_url = url.lower()

    features = {
        "url_length": len(url),
        "has_ip_address": bool(re.match(r'\d+\.\d+\.\d+\.\d+', hostname)),
        "num_subdomains": hostname.count("."),
        "has_at_symbol": "@" in url,
        "has_double_slash_redirect": "//" in path,
        "num_hyphens_in_domain": hostname.count("-"),
        "num_digits_in_domain": sum(c.isdigit() for c in hostname),
        "is_https": parsed.scheme == "https",
        "suspicious_tld": any(full_url.endswith(tld) or f"{tld}/" in full_url for tld in SUSPICIOUS_TLD),
        "is_known_legit": any(legit in hostname for legit in LEGIT_THAI_DOMAINS),
        "has_thai_bank_keyword": bool(re.search(
            r'(kbank|scb|ktb|krungsri|bbl|truemoney|promptpay)', full_url
        )),
        "brand_in_subdomain": bool(re.search(
            r'(paypal|apple|google|facebook|line|true|ais|dtac)', hostname.split(".")[0]
        )),
        "path_has_login": bool(re.search(r'(login|signin|verify|auth|confirm|secure)', path.lower())),
        "excessive_params": url.count("&") > 4,
        "url_contains_hex": bool(re.search(r'%[0-9a-fA-F]{2}', url)),
        "domain_length": len(hostname),
    }
    return features


def compute_phishing_score(features: dict) -> float:
    """
    คำนวณ phishing score จาก features
    คืนค่า 0.0 (ปลอดภัย) ถึง 1.0 (อันตรายมาก)
    """
    if not features:
        return 0.5  # ไม่สามารถวิเคราะห์ได้

    score = 0.0

    # ลดคะแนนถ้าเป็นโดเมนที่รู้จัก
    if features.get("is_known_legit"):
        return 0.05

    # เพิ่มคะแนนความเสี่ยง
    if features.get("has_ip_address"):
        score += 0.35
    if features.get("has_at_symbol"):
        score += 0.30
    if features.get("suspicious_tld"):
        score += 0.25
    if features.get("brand_in_subdomain"):
        score += 0.30
    if features.get("path_has_login"):
        score += 0.20
    if features.get("has_thai_bank_keyword") and not features.get("is_known_legit"):
        score += 0.35  # แอบอ้างธนาคารไทย
    if features.get("url_contains_hex"):
        score += 0.15
    if features.get("excessive_params"):
        score += 0.10
    if features.get("has_double_slash_redirect"):
        score += 0.20
    if not features.get("is_https"):
        score += 0.10
    if features.get("url_length", 0) > 100:
        score += 0.15
    if features.get("num_hyphens_in_domain", 0) > 2:
        score += 0.15
    if features.get("num_subdomains", 0) > 3:
        score += 0.15

    return min(score, 1.0)


def score_to_risk_level(score: float) -> RiskLevel:
    if score >= 0.75:
        return RiskLevel.CRITICAL
    elif score >= 0.50:
        return RiskLevel.HIGH
    elif score >= 0.25:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def generate_url_explanation(features: dict, score: float, risk_level: RiskLevel) -> str:
    reasons = []

    if features.get("is_known_legit"):
        return "โดเมนนี้อยู่ในรายการโดเมนที่รู้จักและน่าเชื่อถือ"

    if features.get("has_ip_address"):
        reasons.append("ใช้ IP address แทนชื่อโดเมน")
    if features.get("has_at_symbol"):
        reasons.append("มีสัญลักษณ์ @ ใน URL ซึ่งน่าสงสัย")
    if features.get("suspicious_tld"):
        reasons.append("ใช้ TLD ที่ไม่น่าเชื่อถือ (.xyz, .top ฯลฯ)")
    if features.get("brand_in_subdomain"):
        reasons.append("มีชื่อแบรนด์ดังใน subdomain (อาจแอบอ้าง)")
    if features.get("has_thai_bank_keyword"):
        reasons.append("มีคำเกี่ยวกับธนาคารไทยใน URL แต่ไม่ใช่โดเมนจริง")
    if features.get("path_has_login"):
        reasons.append("path มีคำที่เกี่ยวกับการล็อกอิน/ยืนยันตัวตน")
    if not features.get("is_https"):
        reasons.append("ไม่ใช้ HTTPS (ไม่เข้ารหัส)")

    if not reasons:
        return f"ระดับความเสี่ยง {risk_level.value.upper()} — ไม่พบรูปแบบอันตรายที่ชัดเจน"

    return f"ระดับความเสี่ยง {risk_level.value.upper()} — {'; '.join(reasons)}"


def analyze_url(url: str) -> dict:
    """วิเคราะห์ URL และคืนผลลัพธ์"""
    features = extract_url_features(url)
    score = compute_phishing_score(features)
    risk_level = score_to_risk_level(score)
    explanation = generate_url_explanation(features, score, risk_level)

    return {
        "url": url,
        "risk_score": round(score, 3),
        "risk_level": risk_level,
        "is_phishing": score >= 0.50,
        "domain_age_days": None,  # จะดึงจาก WHOIS ผ่าน osint_service
        "explanation": explanation,
    }
