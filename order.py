# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import hashlib

# --- 1. CONFIGURATION ---
SHEET_ID = "1Km8Y3C-eW061BEA_wqMx1v655tR0jHeV8jyrY" 
GID_USERS = "0"
GID_CONFIG = "127521360"
GID_PRODUCTS = "2101035544"

# ฟังก์ชันเจนลิงก์แบบเน้นความชัวร์
def get_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={gid}"

@st.cache_data(ttl=10)
def load_data(gid):
    try:
        url = get_url(gid)
        # ใช้เครื่องมืออ่าน CSV ที่ยืดหยุ่นขึ้น
        data = pd.read_csv(url, on_bad_lines='skip')
        return data
    except Exception as e:
        return pd.DataFrame()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 2. SETUP ---
st.set_page_config(page_title="ร้านสหกรณ์จังหวัดตราด จำกัด", layout="wide")

if 'auth' not in st.session_state: 
    st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
if 'cart' not in st.session_state: st.session_state.cart = []

# ดึงข้อมูล
df_users = load_data(GID_USERS)
df_products = load_data(GID_PRODUCTS)
df_config = load_data(GID_CONFIG)

# ตั้งค่าชื่อร้าน
shop_name = "ร้านสหกรณ์จังหวัดตราด จำกัด"
logo_url = None
if not df_config.empty:
    try:
        # ตรวจสอบว่าคอลัมน์ชื่อ key และ value มีอยู่จริง
        shop_name = df_config[df_config['key'] == 'shop_name']['value'].values[0]
        logo_url = df_config[df_config['key'] == 'logo_url']['value'].values[0]
    except: pass

# --- 3. SIDEBAR (แก้เรื่อง Form Error) ---
with st.sidebar:
    if logo_url: 
        st.image(logo_url, use_container_width=True)
    st.title(shop_name)
    
    if not st.session_state.auth["logged_in"]:
        with st.expander("🔐 เข้าสู่ระบบสมาชิก", expanded=False):
            # ย้ำ: ทุกอย่างที่เกี่ยวกับ login ต้องอยู่ใน block 'with st.form'
            with st.form(key="login_panel"):
                input_u = st.text_input("Username")
                input_p = st.text_input("Password", type="password")
                submit_btn = st.form_submit_button("Login")
                
                if submit_btn:
                    if not df_users.empty:
                        # ตรวจสอบรหัสผ่าน
                        match = df_users[(df_users['username'] == input_u) & (df_users['password'] == hash_password(input_p))]
                        if not match.empty:
                            st.session_state.auth = {
                                "logged_in": True, 
                                "user": input_u, 
                                "role": match['role'].values[0]
                            }
                            st.rerun()
                        else:
                            st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
                    else:
                        st.error("ไม่สามารถดึงข้อมูลสมาชิกได้")
    else:
        st.success(f"ผู้ใช้: {st.session_state.auth['user']}")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.rerun()

# --- 4. STOREFRONT ---
st.header(f"🏛️ {shop_name}")
st.divider()

if df_products.empty:
    st.warning("🔄 กำลังเชื่อมต่อข้อมูลสินค้า... หากนานเกินไปโปรดตรวจสอบสถานะการ Share ของ Google Sheets")
else:
    # กรองสินค้า
    try:
        # ปรับการเช็คค่าให้ยืดหยุ่นขึ้น (รองรับทั้ง TRUE/FALSE ตัวเล็กตัวใหญ่)
        show_p = df_products[df_products['is_hidden'].astype(str).str.upper() == 'FALSE']
        
        if show_p.empty:
            st.info("ขณะนี้ยังไม่มีสินค้าวางจำหน่าย")
        else:
            rows_count = (len(show_p) // 3) + 1
            for r in range(rows_count):
                cols = st.columns(3)
                for c in range(3):
                    idx = r * 3 + c
                    if idx < len(show_p):
                        row = show_p.iloc[idx]
                        with cols[c]:
                            with st.container(border=True):
                                if pd.notna(row['image_url']):
                                    st.image(row['image_url'], use_container_width=True)
                                st.subheader(row['name'])
                                if 'caption' in row and pd.notna(row['caption']):
                                    st.write(f"*{row['caption']}*")
                                st.write(f"💰 ราคา: **{row['price']:,}** บาท")
                                
                                if st.session_state.auth["logged_in"]:
                                    if st.button("🛒 เพิ่มลงตะกร้า", key=f"add_{idx}"):
                                        st.session_state.cart.append({"สินค้า": row['name'], "ราคา": row['price']})
                                        st.toast(f"เพิ่ม {row['name']} แล้ว")
                                else:
                                    st.caption("🔒 ล็อกอินเพื่อสั่งซื้อ")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการแสดงสินค้า: {e}")

# ตะกร้าสินค้า
if st.session_state.cart:
    with st.expander("🛒 ตะกร้าของคุณ", expanded=True):
        st.table(pd.DataFrame(st.session_state.cart))
        if st.button("✅ ยืนยันการสั่งซื้อ"):
            st.balloons()
            st.success("รับรายการสั่งซื้อแล้ว!")
            st.session_state.cart = []
