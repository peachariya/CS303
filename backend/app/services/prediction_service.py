import joblib
import re
import os

# กำหนด Path ค้นหาไฟล์โมเดลในโฟลเดอร์ models/ ด้านนอก
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
SMS_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'sms_model.pkl')
URL_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'url_model.pkl')

sms_model = joblib.load(SMS_MODEL_PATH) if os.path.exists(SMS_MODEL_PATH) else None
url_model = joblib.load(URL_MODEL_PATH) if os.path.exists(URL_MODEL_PATH) else None

def predict_sms_risk(text: str) -> int:
    """ตรวจสอบความเสี่ยงข้อความ SMS (0 = ปลอดภัย, 2 = หลอกลวง)"""
    if not sms_model:
        return 0
    length = len(text)
    has_url = 1 if re.search(r'http[s]?://', text) else 0
    risk_words = ['free', 'win', 'urgent', 'prize', 'claim', 'cash', 'refund', 'update']
    risk_word_count = sum(1 for word in risk_words if word in text.lower())
    
    prediction = sms_model.predict([[length, has_url, risk_word_count]])[0]
    return int(prediction)

def predict_url_risk(url: str) -> int:
    """ตรวจสอบความเสี่ยงลิงก์ URL (0 = ปลอดภัย, 1/2 = ฟิชชิ่ง)"""
    if not url_model:
        return 0
    url_length = len(str(url))
    num_dots = str(url).count('.')
    num_hyphens = str(url).count('-')
    sensitive_words = ['login', 'verify', 'update', 'secure', 'account', 'banking']
    has_sensitive_word = 1 if any(word in str(url).lower() for word in sensitive_words) else 0
    
    prediction = url_model.predict([[url_length, num_dots, num_hyphens, has_sensitive_word]])[0]
    return int(prediction)