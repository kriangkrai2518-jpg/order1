# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION (ใช้ ID ใหม่ที่พี่ส่งมาครับ) ---
SHEET_ID = "1KmK8Y3C-eW061BEA_wqMxTw55tER0JHEvBjcyYOg4Vk" 

# GID ของแต่ละหน้า (ตรวจสอบจากรูปพี่อีกครั้ง)
GID_USERS = "0"
GID_CONFIG = "127521360"
GID_PRODUCTS = "2101035544"

def get_url(gid):
    # ใช้ลิงก์รูปแบบทางการของ Google Sheets
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

@st.cache_data(ttl=5)
def load_data(gid):
    try:
        url = get_url(gid)
        return pd.read_csv(url)
    except Exception as e:
        # ถ้ายัง 404 แสดงว่า ID หรือ GID อาจจะมีตัวอักษรผิดไปนิดเดียวครับ
        return pd.DataFrame()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. SETUP ---
st.set_page_config(page_title="ร้านสหกรณ์จังหวัดตราด จำกัด", layout="wide")

if 'auth' not in st.session_state: 
    st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}

df_users = load_data(GID_USERS)
df_products = load_data(GID_PRODUCTS)
df_config = load_data(GID_CONFIG)

# ดึงชื่อร้านจาก Config
shop_name = "ร้านสหกรณ์จังหวัดตราด จำกัด"
if not df_config.empty:
    try:
        shop_name = df_config[df_config['key'] == 'shop_name']['value'].values[0]
    except: pass

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title(f"🏛️ {shop_name}")
    if not st.session_state.auth["logged_in"]:
        with st.form("login_form"):
            st.subheader("🔑 เข้าสู่ระบบ")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if not df_users.empty:
                    # ตรวจสอบกับข้อมูลใน Sheet (admin / kriangkrai)
                    u_match = df_users[(df_users['username'] == u) & (df_users['password'] == hash_password(p))]
                    if not u_match.empty:
                        st.session_state.auth = {"logged_in": True, "user": u, "role": u_match['role'].values[0]}
                        st.rerun()
                    else:
                        st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
                else:
                    st.error("❌ เชื่อมต่อฐานข้อมูลสมาชิกไม่ได้ (เช็ค Sheet ID)")
    else:
        st.success(f"สวัสดี: {st.session_state.auth['user']}")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.rerun()

# --- 4. การแสดงผลสินค้า ---
st.header(shop_name)
st.divider()

if df_products.empty:
    st.error(f"❌ ไม่สามารถดึงข้อมูลสินค้าได้จาก ID: {SHEET_ID}")
    st.info("พี่เกรียงตรวจสอบตัวอักษรใน SHEET_ID อีกครั้งนะครับ ว่าก๊อปมาขาดหรือเกินหรือเปล่า")
else:
    # กรองเฉพาะสินค้าที่ไม่ซ่อน
    visible_p = df_products[df_products['is_hidden'].astype(str).str.lower() == 'false']
    
    cols = st.columns(3)
    for idx, row in visible_p.iterrows():
        with cols[idx % 3]:
            with st.container(border=True):
                if pd.notna(row['image_url']): st.image(row['image_url'], use_container_width=True)
                st.subheader(row['name'])
                if 'caption' in row and pd.notna(row['caption']): st.write(f"*{row['caption']}*")
                st.write(f"💰 ราคา: {row['price']:,} บาท")
                if st.button("🛒 เลือกซื้อ", key=f"p_{idx}"):
                    st.toast(f"เลือก {row['name']} แล้ว")
