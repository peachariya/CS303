import pandas as pd
import os

os.makedirs('data/cleaned', exist_ok=True)
summary_data = []

# --- 1. จัดการข้อมูล SMS (spam.csv) ---
try:
    df_sms = pd.read_csv('data/spam.csv', encoding='latin-1')
    initial_sms = len(df_sms)
    
    # ทำความสะอาดและแปลง Label
    df_sms = df_sms[['v1', 'v2']].rename(columns={'v1': 'label', 'v2': 'text'})
    df_sms['label'] = df_sms['label'].map({'ham': 0, 'spam': 2}) # 0=ปลอดภัย, 2=หลอกลวง
    df_sms.dropna(inplace=True)
    df_sms.drop_duplicates(subset=['text'], inplace=True)
    
    df_sms.to_csv('data/cleaned/cleaned_sms.csv', index=False, encoding='utf-8-sig')
    summary_data.append({'Dataset': 'SMS Spam Collection', 'File Name': 'spam.csv', 'Type': 'SMS', 'Original Rows': initial_sms, 'Cleaned Rows': len(df_sms)})
except Exception as e:
    pass

# --- 2. จัดการข้อมูล URL (PhiUSIIL) ---
try:
    df_url = pd.read_csv('data/PhiUSIIL_Phishing_URL_Dataset.csv')
    initial_url = len(df_url)
    
    # ทำความสะอาด (ลบค่าว่างและ URL ซ้ำ)
    df_url.dropna(subset=['URL', 'label'], inplace=True)
    df_url.drop_duplicates(subset=['URL'], inplace=True)
    
    df_url.to_csv('data/cleaned/cleaned_phiusiil_urls.csv', index=False, encoding='utf-8-sig')
    summary_data.append({'Dataset': 'PhiUSIIL Phishing', 'File Name': 'PhiUSIIL_Phishing_URL_Dataset.csv', 'Type': 'URL', 'Original Rows': initial_url, 'Cleaned Rows': len(df_url)})
except Exception as e:
    pass

# --- 3. จัดการข้อมูล URL (combined_dataset.csv) ---
try:
    df_comb = pd.read_csv('data/combined_dataset.csv')
    initial_comb = len(df_comb)
    
    df_comb.dropna(inplace=True) # ลบแถวที่มีค่าว่างเบื้องต้น
    
    summary_data.append({'Dataset': 'Combined URLs', 'File Name': 'combined_dataset.csv', 'Type': 'URL', 'Original Rows': initial_comb, 'Cleaned Rows': len(df_comb)})
except Exception as e:
    pass

# --- 4. จัดการข้อมูล URL (new_data_urls.csv) ---
try:
    df_new = pd.read_csv('data/new_data_urls.csv')
    initial_new = len(df_new)
    
    df_new.dropna(inplace=True) # ลบแถวที่มีค่าว่างเบื้องต้น
    
    summary_data.append({'Dataset': 'New Data URLs', 'File Name': 'new_data_urls.csv', 'Type': 'URL', 'Original Rows': initial_new, 'Cleaned Rows': len(df_new)})
except Exception as e:
    pass

# --- 5. สร้างไฟล์สรุป Excel ---
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel('Data_Summary_Report.xlsx', index=False)