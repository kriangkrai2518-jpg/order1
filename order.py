# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION (ใช้ ID จากหน้า Publish to the web ที่พี่ส่งมาครับ) ---
# ผมก๊อปค่านี้จากรูปที่พี่ Mark ไว้ เพื่อให้ค่าในระบบ "ตรงกับ Notepad" 100%
PUBLISHED_ID = "2PACX-1vThLBeHbDOBGyXUXKhPLbZpgiouZ36-JDzD6MKF3LQDQo_TyNo4Kll9p2ggX3ECKMfvqYY_31pfJQ3d"

# GID ของแต่ละหน้า (อ้างอิงจากระบบเดิมที่พี่เช็คแล้ว)
GID_USERS = "0"
GID_PRODUCTS = "2101035544"

def get_csv_url(gid):
    # ลิงก์สำหรับดึงข้อมูล CSV จากไฟล์ที่ Publish แล้ว
    return f"https://docs.google.com/spreadsheets/d/e/{PUBLISHED_ID}/pub?gid={gid}&single=true&output=csv"

@st.cache_data(ttl=1)
def load_data(gid):
    try:
        url = get_csv_url(gid)
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# --- 2. SETUP ---
st.set_page_config(page_title="ร้านสหกรณ์จังหวัดตราด จำกัด", layout="wide")

# แสดง ID ที่ระบบกำลังใช้ เพื่อให้พี่เกรียงเทียบกับ Notepad ได้ทันที
st.info(f"🔍 **ID ที่ระบบกำลังใช้:** `{PUBLISHED_ID}`")

df_products = load_data(GID_PRODUCTS)

# --- 3. DISPLAY ---
if df_products.empty:
    st.error("❌ ระบบยังหาไฟล์ไม่เจอ (Error 404)")
    st.write("พี่เกรียงครับ ลองกดปุ่ม **Manage app** -> **Reboot app** เพื่อล้าง ID ชุดเก่าที่มันจำผิดไว้ออกนะครับ")
else:
    st.success("✅ เชื่อมต่อสำเร็จ! ค่าตรงกับที่พี่ Mark ไว้แล้วครับ")
    # แสดงรายการสินค้า
    st.dataframe(df_products)
