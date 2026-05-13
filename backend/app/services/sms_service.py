"""
บริการวิเคราะห์ SMS ภาษาไทยเพื่อตรวจจับข้อความหลอกลวง
ใช้ PyThaiNLP สำหรับ tokenization + TF-IDF + Logistic Regression
"""

import re
import pickle
import os
from typing import List, Tuple

from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np

from app.models.schemas import RiskLevel

# -------------------------------------------------------
# คำศัพท์ที่บ่งชี้การหลอกลวงในบริบทไทย
# -------------------------------------------------------
SCAM_KEYWORDS = {
    "urgent": [
        "ด่วน", "เร่งด่วน", "ทันที", "รีบ", "ภายใน 24 ชั่วโมง",
        "หมดอายุ", "ระงับ", "ถูกระงับ", "โปรดยืนยัน"
    ],
    "impersonation": [
        "กรมสรรพากร", "ตำรวจ", "ศาล", "กระทรวง", "ธนาคารแห่งประเทศไทย",
        "ดีเอสไอ", "ปปง", "DSI", "ธ.ก.ส.", "กสทช"
    ],
    "reward": [
        "ได้รับรางวัล", "โชคดี", "ถูกรางวัล", "รับเงิน", "ฟรี",
        "ไม่มีค่าใช้จ่าย", "แจกเงิน", "โบนัส", "cashback"
    ],
    "threat": [
        "จะถูกดำเนินคดี", "ถูกจับ", "หมายจับ", "บัญชีถูกอายัด",
        "โทษจำคุก", "ค่าปรับ", "แจ้งความ"
    ],
    "link": [
        "คลิก", "กดลิงก์", "ลงทะเบียน", "กรอกข้อมูล",
        "ยืนยันตัวตน", "OTP", "รหัสผ่าน"
    ]
}

STOP_WORDS = set(thai_stopwords())

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ml/sms_model.pkl")


def tokenize_thai(text: str) -> str:
    """ตัดคำภาษาไทยและกรอง stopwords"""
    tokens = word_tokenize(text, engine="newmm")
    tokens = [t for t in tokens if t not in STOP_WORDS and t.strip()]
    return " ".join(tokens)


def detect_suspicious_keywords(text: str) -> Tuple[List[str], List[str]]:
    """
    ตรวจจับคำและรูปแบบที่น่าสงสัยในข้อความ
    คืนค่า: (patterns_found, keywords_found)
    """
    patterns_found = []
    keywords_found = []

    for category, keywords in SCAM_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                keywords_found.append(kw)
                if category not in patterns_found:
                    patterns_found.append(category)

    # ตรวจ URL ที่น่าสงสัย
    url_pattern = re.findall(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        text
    )
    if url_pattern:
        patterns_found.append("suspicious_url")
        keywords_found.extend(url_pattern)

    # ตรวจเบอร์โทรในข้อความ
    phone_pattern = re.findall(r'0[689]\d{8}', text)
    if phone_pattern:
        patterns_found.append("embedded_phone")

    return patterns_found, keywords_found


def load_or_create_model() -> Pipeline:
    """โหลดโมเดลที่ฝึกแล้ว หรือสร้างโมเดล baseline ใหม่"""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)

    # สร้าง pipeline ใหม่ด้วย TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced"
        ))
    ])
    return pipeline


def compute_rule_based_score(patterns: List[str]) -> float:
    """คำนวณ score เบื้องต้นจากกฎ (Rule-based)"""
    weights = {
        "urgent": 0.20,
        "impersonation": 0.30,
        "reward": 0.15,
        "threat": 0.30,
        "link": 0.20,
        "suspicious_url": 0.25,
        "embedded_phone": 0.10,
    }
    score = sum(weights.get(p, 0.05) for p in patterns)
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


def generate_explanation(risk_level: RiskLevel, patterns: List[str], keywords: List[str]) -> str:
    """สร้างคำอธิบายผลการวิเคราะห์ภาษาไทย"""
    pattern_labels = {
        "urgent": "สร้างความเร่งด่วนเทียม",
        "impersonation": "แอบอ้างเป็นหน่วยงานรัฐ",
        "reward": "ล่อใจด้วยรางวัล/เงิน",
        "threat": "ข่มขู่ด้วยผลทางกฎหมาย",
        "link": "ชักชวนให้คลิกลิงก์/กรอกข้อมูล",
        "suspicious_url": "พบ URL น่าสงสัยในข้อความ",
        "embedded_phone": "พบหมายเลขโทรศัพท์ฝังในข้อความ",
    }
    found_labels = [pattern_labels.get(p, p) for p in patterns]

    if not found_labels:
        return "ไม่พบรูปแบบการหลอกลวงที่ชัดเจน ข้อความดูปลอดภัย"

    base = f"ระดับความเสี่ยง: {risk_level.value.upper()} — พบรูปแบบที่น่าสงสัย {len(patterns)} ประเภท: "
    return base + ", ".join(found_labels)


# ------- Public interface -------

def analyze_sms(text: str) -> dict:
    """วิเคราะห์ข้อความ SMS และคืนผลลัพธ์"""
    patterns, keywords = detect_suspicious_keywords(text)
    score = compute_rule_based_score(patterns)
    risk_level = score_to_risk_level(score)
    explanation = generate_explanation(risk_level, patterns, keywords)

    return {
        "text": text,
        "risk_score": round(score, 3),
        "risk_level": risk_level,
        "detected_patterns": patterns,
        "suspicious_keywords": keywords,
        "explanation": explanation,
    }
