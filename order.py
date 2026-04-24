# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION (ใช้ ID จากลิงก์ล่าสุดที่พี่ส่งมาครับ) ---
# ตัวนี้คือ Web ID ที่ได้จาก Publish to the web ของพี่เกรียงเป๊ะๆ
WEB_SHEET_ID = "2PACX-1vThLBeHbDOBGyXUXKhPLbZpgiouZ36-JDzD6MKF3LQDQo_TyNo4Kll9p2ggX3ECKMfvqYY_31pfJQ3d"

# ฟังก์ชันดึงข้อมูลจากลิงก์ Publish โดยตรง (เปลี่ยน format เป็น csv)
def get_web_url(gid):
    return f"https://docs.google.com/spreadsheets/d/e/{WEB_SHEET_ID}/pub?gid={gid}&single=true&output=csv"

# GID ชุดเดิมที่พี่ตรวจสอบแล้ว
GID_USERS = "0"
GID_CONFIG = "127521360"
GID_PRODUCTS = "2101035544"

@st.cache_data(ttl=1)
def load_data(gid):
    try:
        url = get_web_url(gid)
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. SETUP ---
st.set_page_config(page_title="ร้านสหกรณ์จังหวัดตราด จำกัด", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}

# โหลดข้อมูลจาก Web URL
df_users = load_data(GID_USERS)
df_products = load_data(GID_PRODUCTS)

# --- 3. SIDEBAR (Login) ---
with st.sidebar:
    st.title("🏛️ ระบบสมาชิก")
    if not st.session_state.auth["logged_in"]:
        with st.form("login_form"):
            u_in = st.text_input("Username")
            p_in = st.text_input("Password", type="password")
            if st.form_submit_button("เข้าสู่ระบบ"):
                if not df_users.empty:
                    # ตรวจรหัส (พี่พิมพ์รหัสผ่านปกติที่ตั้งไว้)
                    match = df_users[(df_users['username'] == u_in) & 
                                     (df_users['password'] == hash_password(p_in))]
                    if not match.empty:
                        st.session_state.auth = {"logged_in": True, "user": u_in, "role": match['role'].values[0]}
                        st.rerun()
                    else: st.error("❌ ข้อมูลไม่ถูกต้อง")
                else:
                    st.error("⚠️ ระบบเว็บยังไม่ส่งข้อมูลสมาชิกมาให้")
    else:
        st.success(f"ผู้ใช้: {st.session_state.auth['user']}")
        if st.button("🚪 Logout"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.rerun()

# --- 4. DISPLAY ---
st.header("🛒 รายการสินค้าออนไลน์")
st.divider()

if df_products.empty:
    st.warning("🔄 กำลังรอการตอบสนองจาก Google Web...")
    st.info(f"ใช้ Web ID: {WEB_SHEET_ID[:20]}...")
else:
    # แสดงสินค้า
    visible = df_products[df_products['is_hidden'].astype(str).str.lower() == 'false']
    cols = st.columns(3)
    for i, row in visible.iterrows():
        with cols[i % 3]:
            with st.container(border=True):
                if 'image_url' in row and pd.notna(row['image_url']):
                    st.image(row['image_url'], use_container_width=True)
                st.subheader(row['name'])
                st.write(f"ราคา: {row['price']:,} บาท")
                st.button("🛒 เลือก", key=f"p_{i}")
