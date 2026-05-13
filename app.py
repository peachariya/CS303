import streamlit as st
import pandas as pd
import requests
import base64
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import sqlite3
from datetime import datetime

# ==========================================
# 1. การตั้งค่าหน้าเว็บและ Theme
# ==========================================
st.set_page_config(page_title="Cyber Crime Analysis Platform", layout="wide", page_icon="🛡️")
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #0F172A; }
    [data-testid="stSidebar"] * { color: #F1F5F9 !important; }
    h1, h2, h3 { color: #1E293B; font-family: 'Sarabun', sans-serif; }
    .stButton>button { background-color: #2563EB; color: white; border-radius: 8px; width: 100%; border: none;}
    .stButton>button:hover { background-color: #1D4ED8; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ระบบฐานข้อมูล (SQL) สำหรับเก็บ Log
# ==========================================
def init_db():
    conn = sqlite3.connect('crime_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS search_logs
                 (timestamp TEXT, user TEXT, type TEXT, query TEXT, result TEXT)''')
    conn.commit()
    return conn

def add_log(user, search_type, query, result):
    conn = sqlite3.connect('crime_logs.db')
    c = conn.cursor()
    c.execute("INSERT INTO search_logs VALUES (?,?,?,?,?)", 
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, search_type, query, result))
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 3. ฟังก์ชัน Backend (API & ML Mockup)
# ==========================================
def scan_virustotal(url):
    vt_key = "cc372db928245661e7a83f75ae957447bfb1469264795cb5c9bb4a98f1a3bf28"
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    headers = {"accept": "application/json", "x-apikey": vt_key}
    try:
        res = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()['data']['attributes']['last_analysis_stats']
        return None
    except:
        return None

# ==========================================
# 4. ระบบ Login (TU Authentication)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align: center;'>🛡️ ระบบสืบสวนอาชญากรรมไซเบอร์</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>กรุณายืนยันตัวตนด้วยบัญชี @dome.tu.ac.th</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("อีเมลมหาวิทยาลัย:")
        if st.button("เข้าสู่ระบบ"):
            if email.endswith("@dome.tu.ac.th"):
                st.session_state["logged_in"] = True
                st.session_state["user"] = email
                st.rerun()
            else:
                st.error("ปฏิเสธการเข้าถึง: อนุญาตเฉพาะบุคลากร มธ. เท่านั้น")
    st.stop()

# ==========================================
# 5. เมนูหลัก (Main Application)
# ==========================================
st.sidebar.markdown(f"### 👤 {st.session_state['user']}")
st.sidebar.markdown("---")
menu = st.sidebar.radio("โมดูลการทำงาน:", [
    "1️⃣ ตรวจสอบ URL (OSINT)", 
    "2️⃣ วิเคราะห์ข้อความ SMS (NLP)", 
    "3️⃣ วิเคราะห์บัญชีม้า (Link Analysis)",
    "🗄️ ฐานข้อมูลประวัติ (Database)"
])

# --- โมดูล 1: OSINT ---
if menu == "1️⃣ ตรวจสอบ URL (OSINT)":
    st.title("🌐 ตรวจสอบและเปรียบเทียบข้อมูล URL")
    url = st.text_input("ระบุลิงก์ที่ต้องการตรวจสอบ:")
    if st.button("วิเคราะห์ความเสี่ยง"):
        if url:
            with st.spinner("ดึงข้อมูลจาก VirusTotal API..."):
                stats = scan_virustotal(url)
                if stats:
                    st.success("✅ ดึงข้อมูลสำเร็จ")
                    c1, c2, c3 = st.columns(3)
                    c1.error(f"🚨 อันตราย: {stats.get('malicious')}")
                    c2.warning(f"⚠️ น่าสงสัย: {stats.get('suspicious')}")
                    c3.success(f"🛡️ ปลอดภัย: {stats.get('harmless')}")
                    # บันทึกลงฐานข้อมูล
                    add_log(st.session_state['user'], "URL Scan", url, f"Malicious: {stats.get('malicious')}")
                else:
                    st.warning("ไม่พบข้อมูลในฐานข้อมูล")

# --- โมดูล 2: NLP Text Analysis ---
elif menu == "2️⃣ วิเคราะห์ข้อความ SMS (NLP)":
    st.title("💬 ประมวลผลภาษาธรรมชาติ (Thai NLP)")
    st.write("สกัดคุณลักษณะของข้อความเพื่อหาแพตเทิร์น Social Engineering แบบไทย")
    text = st.text_area("วางข้อความ SMS ที่น่าสงสัย:")
    
    if st.button("สกัดคุณลักษณะด้วย Machine Learning"):
        if text:
            # จำลองการทำงานของ PyThaiNLP
            risk_keywords = ["ระงับ", "โอนเงิน", "พัสดุ", "ตำรวจ", "คดี", "ลิงก์", "ติดต่อกลับ"]
            found_words = [word for word in risk_keywords if word in text]
            
            st.subheader("ผลการสกัดคุณลักษณะ (Feature Extraction)")
            st.write(f"**คำเตือนที่พบ (Keywords):** {', '.join(found_words) if found_words else 'ไม่พบคำเสี่ยง'}")
            
            if len(found_words) >= 2:
                st.error("🚨 ระดับความเสี่ยง: สูง (เข้าข่ายแก๊งคอลเซ็นเตอร์ หรือ Scam SMS)")
                add_log(st.session_state['user'], "SMS Scan", text, "High Risk")
            else:
                st.success("✅ ระดับความเสี่ยง: ต่ำ")
                add_log(st.session_state['user'], "SMS Scan", text, "Low Risk")

# --- โมดูล 3: Link Analysis ---
elif menu == "3️⃣ วิเคราะห์บัญชีม้า (Link Analysis)":
    st.title("🕸️ กราฟความสัมพันธ์เส้นทางการเงิน")
    if st.button("ประมวลผลกราฟเครือข่าย"):
        df = pd.DataFrame([
            {"จาก": "นาย A", "ถึง": "บัญชีม้า 01", "ยอดเงิน": 45000},
            {"จาก": "นาง B", "ถึง": "บัญชีม้า 01", "ยอดเงิน": 12000},
            {"จาก": "บัญชีม้า 01", "ถึง": "นายทุน (VIP)", "ยอดเงิน": 57000}
        ])
        
        G = nx.from_pandas_edgelist(df, "จาก", "ถึง", ["ยอดเงิน"], create_using=nx.DiGraph())
        net = Network(height='450px', width='100%', directed=True)
        net.from_nx(G)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
            net.save_graph(tmp.name)
            components.html(open(tmp.name, 'r', encoding='utf-8').read(), height=500)
            add_log(st.session_state['user'], "Link Analysis", "Generated Graph", "Success")

# --- โมดูล 4: Database & Export ---
elif menu == "🗄️ ฐานข้อมูลประวัติ (Database)":
    st.title("🗄️ ประวัติการทำงาน (System Logs)")
    st.write("ข้อมูลถูกบันทึกลงฐานข้อมูล SQL เพื่อการตรวจสอบย้อนหลัง")
    
    conn = sqlite3.connect('crime_logs.db')
    df_logs = pd.read_sql_query("SELECT * FROM search_logs ORDER BY timestamp DESC", conn)
    st.dataframe(df_logs, use_container_width=True)
    
    # ปุ่มดาวน์โหลดรายงาน
    csv = df_logs.to_csv(index=False).encode('utf-8-sig')
    st.download_button(label="📥 ดาวน์โหลดรายงาน (CSV)", data=csv, file_name='investigation_logs.csv', mime='text/csv')

if st.sidebar.button("🚪 ออกจากระบบ"):
    st.session_state["logged_in"] = False
    st.rerun()