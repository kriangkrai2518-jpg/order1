# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION (อัปเดตตามรูป image_893819.jpg ของพี่เกรียง) ---
# ID ที่ถูกต้องต้องไม่มีตัว 't' ข้างหน้านะครับพี่
SHEET_ID = "1KmK8Y3C-eW061BEA_wqMxTw55tER0JHEvBjcyYOg4Vk" 

# GID ชุดล่าสุดที่แกะจาก URL ในรูปของพี่ครับ
GID_USERS = "0"
GID_CONFIG = "127521360"
GID_PRODUCTS = "2101035544"

def get_url(gid):
    # ใช้รูปแบบลิงก์ที่เสถียรที่สุดสำหรับการดึงข้อมูล
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

@st.cache_data(ttl=2) # ลด Cache เหลือ 2 วินาทีเพื่อให้เช็ค Login ได้ทันใจ
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

# โหลดข้อมูล
df_users = load_data(GID_USERS)
df_products = load_data(GID_PRODUCTS)

# --- 3. SIDEBAR (Login) ---
with st.sidebar:
    st.title("🏛️ ระบบสมาชิก")
    if not st.session_state.auth["logged_in"]:
        with st.form("login_form"):
            user_in = st.text_input("Username")
            pass_in = st.text_input("Password", type="password")
            if st.form_submit_button("เข้าสู่ระบบ"):
                if not df_users.empty:
                    # ตรวจสอบ Username และ Password (admin / kriangkrai)
                    # หมายเหตุ: พี่ต้องพิมพ์รหัสผ่านตัวจริง (เช่น admin123) ไม่ใช่รหัสยาวๆ ใน Sheet
                    match = df_users[(df_users['username'] == user_in) & 
                                     (df_users['password'] == hash_password(pass_in))]
                    if not match.empty:
                        st.session_state.auth = {"logged_in": True, "user": user_in, "role": match['role'].values[0]}
                        st.rerun()
                    else: st.error("❌ ข้อมูลไม่ถูกต้อง")
                else: st.error("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลผู้ใช้ได้")
    else:
        st.success(f"ผู้ใช้: {st.session_state.auth['user']}")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.rerun()

# --- 4. MAIN STORE ---
st.header("🛒 รายการสินค้า")
if df_products.empty:
    st.error(f"❌ Error 404: หาไฟล์ Google Sheets ไม่เจอ")
    st.write(f"ID ปัจจุบัน: {SHEET_ID}")
    st.info("พี่เกรียงอย่าลืมกด 'Manage app' -> 'Reboot app' หลังจากแก้โค้ดนะครับ")
else:
    # กรองสินค้า
    visible = df_products[df_products['is_hidden'].astype(str).str.lower() == 'false']
    cols = st.columns(3)
    for i, row in visible.iterrows():
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(row['name'])
                st.write(f"ราคา: **{row['price']:,}** บาท")
                st.button("🛒 เลือก", key=f"buy_{i}")
