import joblib
import re
import os

# ปรับ Path ให้ถอยหลังขึ้นไปหาโฟลเดอร์ models ด้านนอกสุดของโปรเจกต์
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
SMS_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'sms_model.pkl')
URL_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'url_model.pkl')

sms_model = joblib.load(SMS_MODEL_PATH) if os.path.exists(SMS_MODEL_PATH) else None
url_model = joblib.load(URL_MODEL_PATH) if os.path.exists(URL_MODEL_PATH) else None