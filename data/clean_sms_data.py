import pandas as pd
import os

print("เริ่มกระบวนการทำความสะอาดข้อมูล SMS...")

# 1. โหลดข้อมูล (ไฟล์ spam.csv จาก Kaggle มักใช้การเข้ารหัสแบบ latin-1)
file_path = 'data/spam.csv'
try:
    df = pd.read_csv(file_path, encoding='latin-1')
except FileNotFoundError:
    print(f"ไม่พบไฟล์ที่ {file_path} กรุณาตรวจสอบว่าย้ายไฟล์เข้าโฟลเดอร์ data แล้ว")
    exit()

initial_count = len(df)
print(f"-> โหลดข้อมูลสำเร็จ จำนวนเริ่มต้น: {initial_count} แถว")

# 2. คัดเฉพาะคอลัมน์ที่ใช้งานและเปลี่ยนชื่อ (v1 คือ label, v2 คือข้อความ)
df = df[['v1', 'v2']]
df.rename(columns={'v1': 'label', 'v2': 'text'}, inplace=True)

# 3. จัดการ Label ให้เป็นตัวเลขระดับความเสี่ยง
# ham (ปกติ) = 0 (ปลอดภัย), spam (สแปม) = 2 (หลอกลวง)
df['label'] = df['label'].map({'ham': 0, 'spam': 2})

# 4. ลบข้อมูลว่างและลบข้อความที่ซ้ำซ้อน
df.dropna(inplace=True)
df.drop_duplicates(subset=['text'], inplace=True)

final_count = len(df)
print(f"-> จำนวนหลังทำความสะอาดและลบตัวซ้ำ: {final_count} แถว (ลบออก {initial_count - final_count} แถว)")

# 5. บันทึกไฟล์ที่คลีนแล้ว
os.makedirs('data/cleaned', exist_ok=True)
output_path = 'data/cleaned/cleaned_sms_data.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"บันทึกไฟล์พร้อมใช้งานไปที่: {output_path}")