# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION ---
# ID ตัวนี้ผมก๊อปมาจาก Notepad ในรูป image_88cf39.jpg ของพี่เลยครับ
SHEET_ID = "1KmK8Y3C-eW061BEA_wqMxTw55tER0JHEvBjcyYOg4Vk" 

# GID ตามหน้าจอจริงของพี่เกรียง
GID_USERS = "0"
GID_CONFIG = "127521360"
GID_PRODUCTS = "2101035544"

def get_url(gid):
    # ใช้ลิงก์รูปแบบ CSV Export ที่เสถียรที่สุด
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

@st.cache_data(ttl=1)
def load_data(gid):
    try:
        url = get_url(gid)
        return pd.read_csv(url)
    except Exception as e:
        return pd.DataFrame()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. SETUP ---
st.set_page_config(page_title="James Shop V6.3", layout="wide")
if 'auth' not in st.session_state: 
    st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}

# ดึงข้อมูลมาเช็ค
df_users = load_data(GID_USERS)
df_products = load_data(GID_PRODUCTS)

# --- 3. SIDEBAR (Login) ---
with st.sidebar:
    st.title("🏛️ เข้าสู่ระบบ")
    if not st.session_state.auth["logged_in"]:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if not df_users.empty:
                    # เทียบ Username และ Password (ที่ Hash แล้ว)
                    match = df_users[(df_users['username'] == u) & (df_users['password'] == hash_password(p))]
                    if not match.empty:
                        st.session_state.auth = {"logged_in": True, "user": u, "role": match['role'].values[0]}
                        st.rerun()
                    else: st.error("❌ ข้อมูลไม่ถูกต้อง")
                else: st.error("⚠️ ต่อฐานข้อมูลไม่ได้ เช็คการ Share ไฟล์ครับ")
    else:
        st.write(f"สวัสดี: **{st.session_state.auth['user']}**")
        if st.button("Logout"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.rerun()

# --- 4. MAIN DISPLAY ---
st.header("🛒 รายการสินค้า")
if df_products.empty:
    st.error(f"❌ ยังเชื่อมต่อไม่ได้ (Error 404)")
    st.info(f"ID ที่แอปมองเห็น: {SHEET_ID}")
    st.warning("พี่เกรียงอย่าลืมกดปุ่ม Share (สีฟ้า) -> เปลี่ยนเป็น Anyone with the link นะครับ")
else:
    st.success("✅ เชื่อมต่อสำเร็จ!")
    # กรองสินค้าและแสดงผล
    show = df_products[df_products['is_hidden'].astype(str).str.lower() == 'false']
    st.dataframe(show)
