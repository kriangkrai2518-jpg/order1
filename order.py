# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION (ล้าง ID ให้เหลือแต่ตัวที่ถูกต้องเป๊ะๆ ครับ) ---
# ผมตัดตัว 'K' ที่เกินมาออกให้แล้วครับพี่เกรียง
SHEET_ID = "1Km8Y3C-eW061BEA_wqMxTw55tER0JHEvBjcyYOg4Vk" 

# GID ชุดเดิมที่พี่ตรวจสอบแล้วว่าถูกต้อง
GID_USERS = "0"
GID_CONFIG = "127521360"
GID_PRODUCTS = "2101035544"

def get_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

@st.cache_data(ttl=1) # บังคับดึงข้อมูลใหม่ทุก 1 วินาทีเพื่อเช็คผล
def load_data(gid):
    try:
        return pd.read_csv(get_url(gid))
    except:
        return pd.DataFrame()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. SETUP ---
st.set_page_config(page_title="ร้านสหกรณ์จังหวัดตราด จำกัด", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}

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
                    # ตรวจรหัสผ่าน (พี่พิมพ์ admin123 นะครับ อย่าพิมพ์รหัสยาวๆ)
                    match = df_users[(df_users['username'] == u_in) & 
                                     (df_users['password'] == hash_password(p_in))]
                    if not match.empty:
                        st.session_state.auth = {"logged_in": True, "user": u_in, "role": match['role'].values[0]}
                        st.rerun()
                    else: st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านผิด")
                else: st.error("⚠️ เชื่อมต่อข้อมูลผู้ใช้ไม่ได้ (เช็ค ID/GID)")
    else:
        st.write(f"สวัสดีคุณ: **{st.session_state.auth['user']}**")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.rerun()

# --- 4. DISPLAY ---
st.header("🛒 รายการสินค้า")
if df_products.empty:
    st.error(f"❌ ยังหาไฟล์ไม่เจอ (ID: {SHEET_ID})")
    st.info("พี่เกรียงอย่าลืม Reboot app หลังจากแก้โค้ดเสร็จนะครับ")
else:
    # แสดงสินค้า
    visible = df_products[df_products['is_hidden'].astype(str).str.lower() == 'false']
    cols = st.columns(3)
    for i, row in visible.iterrows():
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(row['name'])
                st.write(f"ราคา: {row['price']:,} บาท")
                st.button("เลือกสินค้า", key=f"b_{i}")
