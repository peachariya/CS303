import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

print("=== เริ่มกระบวนการเทรนโมเดลสำหรับ SMS ===")
try:
    # 1. โหลดข้อมูล SMS ที่สกัดฟีเจอร์แล้ว
    df_sms = pd.read_csv('data/featured/featured_sms.csv')
    
    # กำหนด Features (ตัวแปรต้น) และ Target (ตัวแปรเป้าหมายคือ label 0 หรือ 2)
    X_sms = df_sms[['msg_length', 'has_url', 'risk_word_count']]
    y_sms = df_sms['label']
    
    # แบ่งข้อมูลสำหรับ Train และ Test (80% เทรน, 20% ทดสอบ)
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X_sms, y_sms, test_size=0.2, random_state=42)
    
    # 2. สร้างและเทรนโมเดล Random Forest
    model_sms = RandomForestClassifier(random_state=42)
    model_sms.fit(X_train_s, y_train_s)
    
    # 3. ประเมินผลโมเดล SMS
    y_pred_s = model_sms.predict(X_test_s)
    print(f"ความแม่นยำของโมเดล SMS (Accuracy): {accuracy_score(y_test_s, y_pred_s):.4f}")
    print("รายงานผลการจำแนกประเภท SMS:")
    print(classification_report(y_test_s, y_pred_s))

except Exception as e:
    print(f"ข้ามการเทรน SMS เนื่องจาก: {e}")

print("\n=== เริ่มกระบวนการเทรนโมเดลสำหรับ URL ===")
try:
    # 1. โหลดข้อมูล URL ที่สกัดฟีเจอร์แล้ว
    df_url = pd.read_csv('data/featured/featured_urls.csv')
    
    # กำหนด Features และ Target สำหรับ URL
    X_url = df_url[['url_length', 'num_dots', 'num_hyphens', 'has_sensitive_word']]
    y_url = df_url['label']
    
    # สุ่มตัวอย่างมาเทรนบางส่วน (เช่น 50,000 แถวแรก) เพื่อความรวดเร็ว
    if len(df_url) > 50000:
        df_url_sample = df_url.sample(n=50000, random_state=42)
        X_url = df_url_sample[['url_length', 'num_dots', 'num_hyphens', 'has_sensitive_word']]
        y_url = df_url_sample['label']

    X_train_u, X_test_u, y_train_u, y_test_u = train_test_split(X_url, y_url, test_size=0.2, random_state=42)
    
    # 2. สร้างและเทรนโมเดล URL
    model_url = RandomForestClassifier(random_state=42)
    model_url.fit(X_train_u, y_train_u)
    
    # 3. ประเมินผลโมเดล URL
    y_pred_u = model_url.predict(X_test_u)
    print(f"ความแม่นยำของโมเดล URL (Accuracy): {accuracy_score(y_test_u, y_pred_u):.4f}")
    print("รายงานผลการจำแนกประเภท URL:")
    print(classification_report(y_test_u, y_pred_u))

except Exception as e:
    print(f"ข้ามการเทรน URL เนื่องจาก: {e}")

# ==========================================
# บันทึกโมเดล (Model Serialization)
# ==========================================
print("\n💾 กำลังบันทึกโมเดล...")
os.makedirs('models', exist_ok=True)  # สร้างโฟลเดอร์ models ถ้ายังไม่มี

# เซฟไฟล์โมเดล SMS และ URL
joblib.dump(model_sms, 'models/sms_model.pkl')
joblib.dump(model_url, 'models/url_model.pkl')

print("✅ บันทึกไฟล์โมเดลลงในโฟลเดอร์ models/ เรียบร้อยแล้ว")