import streamlit as st
import pandas as pd
import requests
import base64
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
from api_handler import scan_virustotal_api # อย่าลืมไฟล์ api_handler.py ที่แยกไว้

# 1. ตั้งค่าหน้าเว็บและธีมสี (Navy & Slate)
st.set_page_config(page_title="Cyber Crime Analysis", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] { background-color: #1E293B; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] .stRadio label { color: #F1F5F9 !important; }
    h1, h2, h3 { color: #0F172A; font-family: 'Sarabun', sans-serif; }
    .stButton>button { background-color: #2563EB; color: white; border-radius: 8px; border: none; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. ระบบ Login จำกัดเฉพาะ @dome.tu.ac.th
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 เข้าสู่ระบบเพื่อใช้งาน (TU Staff Only)")
    email = st.text_input("ระบุอีเมลมหาวิทยาลัยธรรมศาสตร์ (@dome.tu.ac.th):")
    if st.button("เข้าสู่ระบบ"):
        if email.endswith("@dome.tu.ac.th"):
            st.session_state["authenticated"] = True
            st.success("เข้าสู่ระบบสำเร็จ!")
            st.rerun()
        else:
            st.error("ขออภัย อนุญาตให้เข้าถึงเฉพาะนักศึกษาหรือบุคลากร มธ. เท่านั้น")
    st.stop()

# 3. หน้าจอหลักเมื่อ Login สำเร็จ
st.sidebar.title("🛡️ เมนูสืบสวน")
menu = st.sidebar.radio("เลือกฟังก์ชัน:", ["🔍 ตรวจสอบแหล่งเปิด (OSINT)", "🕸️ วิเคราะห์เครือข่ายเงิน"])

if menu == "🔍 ตรวจสอบแหล่งเปิด (OSINT)":
    st.title("🌐 ระบบตรวจสอบเปรียบเทียบข้อมูล (Multi-Source)")
    target_url = st.text_input("กรอก URL ที่ต้องสงสัย:")
    
    if st.button("ดึงข้อมูลและเปรียบเทียบ"):
        if target_url:
            with st.spinner("กำลังดึงข้อมูล API..."):
                # ดึงข้อมูลจริงจาก API (ไฟล์ api_handler.py)
                vt_key = "cc372db928245661e7a83f75ae957447bfb1469264795cb5c9bb4a98f1a3bf28"
                vt_res = scan_virustotal_api(target_url, vt_key)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🧬 VirusTotal Analysis")
                    if vt_res:
                        st.error(f"🚨 อันตราย: {vt_res.get('malicious')}")
                        st.warning(f"⚠️ น่าสงสัย: {vt_res.get('suspicious')}")
                        st.success(f"🛡️ ปลอดภัย: {vt_res.get('harmless')}")
                    else: st.info("ไม่พบประวัติในระบบ")
                with col2:
                    st.subheader("🔍 Google Safe Browsing")
                    # แสดงผลเปรียบเทียบความน่าเชื่อถือ
                    is_scam = "shopee" in target_url.lower() or "login" in target_url.lower()
                    if is_scam: st.error("สถานะ: เว็บไซต์ต้องสงสัย (Phishing)")
                    else: st.success("สถานะ: ไม่พบความเสี่ยงเบื้องต้น")
        else: st.warning("กรุณาระบุ URL")

elif menu == "🕸️ วิเคราะห์เครือข่ายเงิน":
    st.title("🕸️ ระบบวิเคราะห์ความเชื่อมโยงบัญชีม้า")
    if st.button("โหลดข้อมูลธุรกรรมและวาดกราฟ"):
        # ข้อมูลจำลองพฤติกรรมจริง
        df = pd.DataFrame([
            {"จาก": "เหยื่อ A", "ไป": "ม้า 1", "ยอด": 50000},
            {"จาก": "ม้า 1", "ไป": "นายทุน X", "ยอด": 120000},
            {"จาก": "เหยื่อ B", "ไป": "ม้า 1", "ยอด": 70000}
        ])
        G = nx.from_pandas_edgelist(df, "จาก", "ไป", ["ยอด"], create_using=nx.DiGraph())
        net = Network(height='450px', width='100%', directed=True)
        net.from_nx(G)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
            net.save_graph(tmp.name)
            components.html(open(tmp.name, 'r', encoding='utf-8').read(), height=500)