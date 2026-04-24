# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION (ใช้ค่าจากลิงก์ล่าสุดที่พี่ Mark ไว้ครับ) ---
# ผมก๊อปค่า 2PACX... จากรูป image_88b98e.jpg ของพี่มาวางให้ตรงเป๊ะแล้วครับ
FINAL_WEB_ID = "2PACX-1vThLBeHbDOBGyXUXKhPLbZpgiouZ36-JDzD6MKF3LQDQo_TyNo4Kll9p2ggX3ECKMfvqYY_31pfJQ3d"

# GID ของแต่ละหน้า (เช็คจาก Tabs ด้านล่างใน Google Sheet ของพี่)
GID_USERS = "0"
GID_PRODUCTS = "2101035544"

def get_web_url(gid):
    # ลิงก์ดึงข้อมูลแบบ CSV จากหน้าเว็บที่ Publish แล้ว (วิธีที่ปลอดภัยที่สุด)
    return f"https://docs.google.com/spreadsheets/d/e/{FINAL_WEB_ID}/pub?gid={gid}&single=true&output=csv"

@st.cache_data(ttl=1)
def load_data(gid):
    try:
        url = get_web_url(gid)
        # ลองดึงข้อมูล
        return pd.read_csv(url)
    except Exception as e:
        return pd.DataFrame()

# --- 2. SETUP PAGE ---
st.set_page_config(page_title="ร้านสหกรณ์จังหวัดตราด จำกัด", layout="wide")

# แสดงผลตรวจสอบบนหน้าจอเพื่อให้พี่เกรียงมั่นใจว่า ID ตรงกับที่ Mark ไว้
st.info(f"🔍 **ID ที่ระบบกำลังใช้:** `{FINAL_WEB_ID}`")

df_products = load_data(GID_PRODUCTS)

# --- 3. MAIN DISPLAY ---
if df_products.empty:
    st.error("❌ ระบบยังเข้าถึงข้อมูลไม่ได้ (Error 404)")
    st.write("1. พี่เกรียงตรวจสอบว่าใน Google Sheet ยังกด 'Publish' อยู่ไหม")
    st.write("2. ลองกดปุ่ม **Manage app** -> **Reboot app** เพื่อล้างค่าเก่าครับ")
else:
    st.success("✅ เชื่อมต่อสำเร็จ! ข้อมูลในระบบตรงกับ Google Sheet แล้วครับ")
    st.dataframe(df_products)
