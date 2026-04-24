# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib
import re

# --- 1. CONFIGURATION ---
SHEET_ID = "1Km8Y3C-eW061BEA_wqMx1v655tR0jHeV8jyrY" 
GID_USERS = "0"
GID_CONFIG = "127521360"
GID_PRODUCTS = "2101035544"

# ฟังก์ชันแปลงลิงก์ Google Drive ให้เป็น Direct Link (สำคัญมากครับพี่เกรียง)
def fix_drive_link(link):
    if not isinstance(link, str): return link
    # ถ้าเป็นลิงก์ Google Drive แบบ /file/d/.../view
    if "drive.google.com" in link and "/file/d/" in link:
        file_id = re.search(r"/file/d/([^/]+)", link)
        if file_id:
            return f"https://drive.google.com/uc?export=view&id={file_id.group(1)}"
    return link

def get_url(gid):
    # ปรับรูปแบบลิงก์ดึงข้อมูล CSV ให้เสถียรที่สุด
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

@st.cache_data(ttl=10)
def load_data(gid):
    try:
        url = get_url(gid)
        data = pd.read_csv(url)
        # แก้ไขลิงก์รูปภาพในตารางทันทีที่โหลดมา
        if 'image_url' in data.columns:
            data['image_url'] = data['image_url'].apply(fix_drive_link)
        if 'value' in data.columns: # สำหรับหน้า config (logo_url)
            data['value'] = data['value'].apply(fix_drive_link)
        return data
    except:
        return pd.DataFrame()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. SETUP ---
st.set_page_config(page_title="ร้านสหกรณ์จังหวัดตราด จำกัด", layout="wide")

if 'auth' not in st.session_state: 
    st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
if 'cart' not in st.session_state: st.session_state.cart = []

# โหลดข้อมูล
df_users = load_data(GID_USERS)
df_products = load_data(GID_PRODUCTS)
df_config = load_data(GID_CONFIG)

# ตั้งค่าชื่อร้านและโลโก้
shop_name = "ร้านสหกรณ์จังหวัดตราด จำกัด"
logo_url = None
if not df_config.empty:
    try:
        shop_name = df_config[df_config['key'] == 'shop_name']['value'].values[0]
        logo_url = df_config[df_config['key'] == 'logo_url']['value'].values[0]
    except: pass

# --- 3. SIDEBAR (เมนูหลัก) ---
with st.sidebar:
    if logo_url: st.image(logo_url, use_container_width=True)
    st.title(shop_name)
    
    if not st.session_state.auth["logged_in"]:
        with st.form("login_section"): # ย้ายทุกอย่างเข้าใน form
            st.subheader("🔐 เข้าสู่ระบบ")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if not df_users.empty:
                    u_match = df_users[(df_users['username'] == u) & (df_users['password'] == hash_password(p))]
                    if not u_match.empty:
                        st.session_state.auth = {"logged_in": True, "user": u, "role": u_match['role'].values[0]}
                        st.rerun()
                    else: st.error("ชื่อผู้ใช้หรือรหัสผ่านผิด")
    else:
        st.write(f"ผู้ใช้: **{st.session_state.auth['user']}**")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.rerun()

# --- 4. การแสดงผลหน้าบ้าน ---
st.header(shop_name)
st.divider()

if df_products.empty:
    st.error("❌ ไม่สามารถดึงข้อมูลจาก Google Sheets ได้ (Error 404)")
    st.info("พี่เกรียงลองกด 'Publish to the web' ในไฟล์ Google Sheet เพิ่มอีกทางหนึ่งครับ (File > Share > Publish to the web)")
else:
    # กรองสินค้า (รองรับ FALSE/false)
    visible_p = df_products[df_products['is_hidden'].astype(str).str.lower() == 'false']
    
    cols = st.columns(3)
    for idx, row in visible_p.iterrows():
        with cols[idx % 3]:
            with st.container(border=True):
                if pd.notna(row['image_url']): st.image(row['image_url'], use_container_width=True)
                st.subheader(row['name'])
                if 'caption' in row and pd.notna(row['caption']): st.write(f"*{row['caption']}*")
                st.write(f"💰 ราคา: {row['price']:,} บาท")
                
                if st.session_state.auth["logged_in"]:
                    if st.button("🛒 เพิ่มลงตะกร้า", key=f"buy_{idx}"):
                        st.session_state.cart.append({"สินค้า": row['name'], "ราคา": row['price']})
                        st.toast(f"เพิ่ม {row['name']} แล้ว")
                else:
                    st.caption("🔒 กรุณา Login เพื่อซื้อ")

# ตะกร้าสินค้า
if st.session_state.cart:
    with st.expander("🛒 ตะกร้าสินค้าของคุณ", expanded=True):
        st.table(pd.DataFrame(st.session_state.cart))
        if st.button("✅ ยืนยันคำสั่งซื้อ"):
            st.balloons()
            st.success("ขอบคุณครับ!")
            st.session_state.cart = []
