# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION (เชื่อมต่อกับ Sheet ของพี่เกรียง) ---
SHEET_ID = "1Km8Y3C-eW061BEA_wqMx1v655tR0jHeV8jyrY" 

# เลข GID ที่ดึงจากรูปภาพของพี่
GID_USERS = "0"
GID_CONFIG = "127521360"
GID_PRODUCTS = "2101035544"

def get_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

@st.cache_data(ttl=60) # อัปเดตข้อมูลทุก 1 นาที
def load_data(gid):
    try:
        return pd.read_csv(get_url(gid))
    except Exception as e:
        st.error(f"เชื่อมต่อข้อมูลไม่ได้: {e}")
        return pd.DataFrame()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. เริ่มต้นระบบ ---
st.set_page_config(page_title="James Online Shop", layout="wide")

if 'auth' not in st.session_state: 
    st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
if 'cart' not in st.session_state: st.session_state.cart = []

# ดึงข้อมูลจาก Cloud
df_users = load_data(GID_USERS)
df_products = load_data(GID_PRODUCTS)
df_config = load_data(GID_CONFIG)

# ตั้งค่าชื่อร้านและโลโก้จาก Sheet Config
shop_name = "James Shop"
logo_url = ""
if not df_config.empty:
    try:
        shop_name = df_config[df_config['key'] == 'shop_name']['value'].values[0]
        logo_url = df_config[df_config['key'] == 'logo_url']['value'].values[0]
    except: pass

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    if logo_url: st.image(logo_url, use_container_width=True)
    st.title(shop_name)
    
    if not st.session_state.auth["logged_in"]:
        with st.expander("🔐 เข้าสู่ระบบ"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user_match = df_users[(df_users['username'] == u) & (df_users['password'] == hash_password(p))]
                if not user_match.empty:
                    st.session_state.auth = {"logged_in": True, "user": u, "role": user_match['role'].values[0]}
                    st.rerun()
                else: st.error("รหัสผ่านไม่ถูกต้อง")
    else:
        st.write(f"สวัสดีคุณ: **{st.session_state.auth['user']}**")
        st.caption(f"สถานะ: {st.session_state.auth['role']}")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.session_state.cart = []
            st.rerun()

# --- 4. STOREFRONT DISPLAY ---
st.title(shop_name)
st.divider()

if df_products.empty:
    st.info("กำลังโหลดข้อมูลสินค้า...")
else:
    cols = st.columns(3)
    # แสดงเฉพาะสินค้าที่ไม่ถูกซ่อน
    visible_p = df_products[df_products['is_hidden'] == False]
    
    for idx, row in visible_p.iterrows():
        with cols[idx % 3]:
            with st.container(border=True):
                # รูปภาพ
                if pd.notna(row['image_url']): st.image(row['image_url'], use_container_width=True)
                # ชื่อและคำบรรยาย
                st.subheader(row['name'])
                if 'caption' in row and pd.notna(row['caption']):
                    st.write(f"*{row['caption']}*")
                # ราคา
                st.write(f"ราคา: **{row['price']:,} บาท**")
                
                if st.session_state.auth["logged_in"]:
                    if st.button("🛒 เพิ่มลงตะกร้า", key=f"btn_{idx}"):
                        st.session_state.cart.append({"name": row['name'], "price": row['price']})
                        st.toast(f"เพิ่ม {row['name']} แล้ว")
                else:
                    st.caption("🔒 กรุณา Login เพื่อสั่งซื้อ")

# แสดงตะกร้าสินค้าถ้ามีการเลือก
if st.session_state.cart:
    with st.expander("🛒 ตะกร้าสินค้าของคุณ", expanded=True):
        cart_df = pd.DataFrame(st.session_state.cart)
        st.table(cart_df)
        st.subheader(f"รวมทั้งสิ้น: {cart_df['price'].sum():,} บาท")
        if st.button("✅ ยืนยันการสั่งซื้อ"):
            st.success("ส่งรายการสั่งซื้อเรียบร้อย!")
            st.session_state.cart = []
