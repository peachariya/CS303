import pandas as pd
import re
import os

print("เริ่มกระบวนการสกัดฟีเจอร์ (Feature Engineering)...")
os.makedirs('data/featured', exist_ok=True)

# ==========================================
# 1. สกัดฟีเจอร์สำหรับ SMS
# ==========================================
try:
    print("กำลังสกัดฟีเจอร์ฝั่ง SMS...")
    df_sms = pd.read_csv('data/cleaned/cleaned_sms.csv')
    
    # ฟีเจอร์ที่ 1: ความยาวของข้อความ (สแปมมักจะยาวกว่าปกติ)
    df_sms['msg_length'] = df_sms['text'].apply(len)
    
    # ฟีเจอร์ที่ 2: ตรวจสอบการมีลิงก์ในข้อความ (1 = มีลิงก์, 0 = ไม่มีลิงก์)
    def has_url(text):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[^\s]+')
        return 1 if url_pattern.search(str(text)) else 0
    df_sms['has_url'] = df_sms['text'].apply(has_url)
    
    # ฟีเจอร์ที่ 3: นับคำเสี่ยง (Risk Keywords) สำหรับภาษาอังกฤษ
    risk_words = ['free', 'win', 'urgent', 'prize', 'claim', 'cash', 'refund', 'update']
    def count_risk_words(text):
        text_lower = str(text).lower()
        return sum(1 for word in risk_words if word in text_lower)
    df_sms['risk_word_count'] = df_sms['text'].apply(count_risk_words)

    df_sms.to_csv('data/featured/featured_sms.csv', index=False, encoding='utf-8-sig')
    print("-> สร้างฟีเจอร์ SMS สำเร็จ! บันทึกที่ data/featured/featured_sms.csv")
except Exception as e:
    print(f"เกิดข้อผิดพลาดกับฝั่ง SMS: {e}")

# ==========================================
# 2. สกัดฟีเจอร์สำหรับ URL (PhiUSIIL)
# ==========================================
try:
    print("\nกำลังสกัดฟีเจอร์ฝั่ง URL...")
    df_url = pd.read_csv('data/cleaned/cleaned_phiusiil_urls.csv')
    
    # ฟีเจอร์ที่ 1: ความยาวของ URL (ลิงก์หลอกลวงมักจะซ่อนโดเมนย่อยให้ยาวๆ)
    df_url['url_length'] = df_url['URL'].apply(lambda x: len(str(x)))
    
    # ฟีเจอร์ที่ 2: จำนวนจุด (.) ในลิงก์ (โดเมนจริงมักมีจุดไม่เยอะ)
    df_url['num_dots'] = df_url['URL'].apply(lambda x: str(x).count('.'))
    
    # ฟีเจอร์ที่ 3: จำนวนขีดกลาง (-) ในลิงก์
    df_url['num_hyphens'] = df_url['URL'].apply(lambda x: str(x).count('-'))
    
    # ฟีเจอร์ที่ 4: ตรวจพบคำหลอกให้เชื่อถือ (Sensitive Words)
    sensitive_words = ['login', 'verify', 'update', 'secure', 'account', 'banking']
    def has_sensitive_word(url):
        url_lower = str(url).lower()
        return 1 if any(word in url_lower for word in sensitive_words) else 0
    df_url['has_sensitive_word'] = df_url['URL'].apply(has_sensitive_word)

    df_url.to_csv('data/featured/featured_urls.csv', index=False, encoding='utf-8-sig')
    print("-> สร้างฟีเจอร์ URL สำเร็จ! บันทึกที่ data/featured/featured_urls.csv")
except Exception as e:
    print(f"เกิดข้อผิดพลาดกับฝั่ง URL: {e}")

print("\n✅ เสร็จสิ้นกระบวนการ Improvement เตรียมเข้าสู่การ Train Model ได้เลย!")