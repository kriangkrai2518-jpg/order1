# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION (ใช้ค่าจากลิงก์ Publish to the web ที่พี่ส่งมาล่าสุด) ---
# ตัวนี้คือ ID สำหรับดึงข้อมูลผ่านเว็บครับ
WEB_ID = "2PACX-1vThLBeHbDOBGyXUXKhPLbZpgiouZ36-JDzD6MKF3LQDQo_TyNo4Kll9p2ggX3ECKMfvqYY_31pfJQ3d"

# GID ของแต่ละหน้า (เช็คจาก Google Sheet ของพี่อีกทีนะครับ)
GID_USERS = "0"
GID_PRODUCTS = "2101035544"

def get_web_url(gid):
    # ลิงก์ดึงข้อมูลแบบ CSV จากหน้าเว็บที่ Publish แล้ว
    return f"https://docs.google.com/spreadsheets/d/e/{WEB_ID}/pub?gid={gid}&single=true&output=csv"

@st.cache_data(ttl=1)
def load_data(gid):
    try:
        url = get_web_url(gid)
        return pd.read_csv(url)
    except Exception as e:
        return pd.DataFrame()

# --- 2. SETUP ---
st.set_page_config(page_title="ร้านสหกรณ์จังหวัดตราด จำกัด", layout="wide")

# แสดง ID ที่ระบบใช้อยู่ปัจจุบันให้พี่ตรวจสอบบนหน้าจอแอปเลยครับ
st.info(f"🔍 **ตรวจสอบ ID ปัจจุบัน:** `{WEB_ID}`")

df_products = load_data(GID_PRODUCTS)

# --- 3. DISPLAY ---
if df_products.empty:
    st.error("❌ ระบบยังเชื่อมต่อกับ Google Sheet ไม่ได้ (Error 404)")
    st.warning("พี่เกรียงครับ รบกวนกดปุ่ม 'Manage app' -> 'Reboot app' ในหน้า Streamlit Cloud 1 ครั้งครับ")
else:
    st.success("✅ เชื่อมต่อสำเร็จ! ข้อมูลตรงกันแล้วครับ")
    # แสดงรายการสินค้า
    st.dataframe(df_products)
