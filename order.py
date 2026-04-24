# -*- coding: utf-8 -*-
import streamlit as st
import json
import hashlib
from pathlib import Path

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="James Shop V4.0", layout="wide")

IMG_DIR = Path("shop_images")
IMG_DIR.mkdir(exist_ok=True)
DB_FILE = Path("shop_db.json")
CONFIG_FILE = Path("shop_config.json")
USER_FILE = Path("users.json")  # เก็บทั้ง Admin และ Member


# ฟังก์ชันความปลอดภัย
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def load_users():
    if USER_FILE.exists():
        with open(USER_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    # เริ่มต้นมีแค่ admin หลัก (User: admin / Pass: admin123)
    return {"admin": {"pass": hash_password("admin123"), "role": "admin"}}


def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def load_db():
    if DB_FILE.exists():
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                pass
    return {"logo": None, "shop_name": "James Factory Shop"}


# --- Load Data ---
db = load_db()
config = load_config()
users = load_users()

# Session States
if 'auth' not in st.session_state: st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
if 'cart' not in st.session_state: st.session_state.cart = []

# --- 2. SIDEBAR NAVIGATION & AUTH ---
with st.sidebar:
    if config["logo"] and Path(config["logo"]).exists():
        st.image(config["logo"], use_container_width=True)

    st.title("Main Menu")

    # กำหนดเมนูตาม Role
    menu = ["🏠 หน้าบ้าน (Storefront)"]
    if st.session_state.auth["role"] == "admin":
        menu += ["⚙️ หลังบ้าน (Admin Panel)", "👥 จัดการสมาชิก/Admin"]

    choice = st.radio("ไปที่หน้า:", menu)
    st.divider()

    # Login / Logout Section
    if not st.session_state.auth["logged_in"]:
        with st.expander("🔐 เข้าสู่ระบบ / สมัครสมาชิก"):
            tab_l, tab_s = st.tabs(["Login", "Signup"])
            with tab_l:
                with st.form("login_f"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")
                    if st.form_submit_button("เข้าสู่ระบบ"):
                        if u in users and users[u]["pass"] == hash_password(p):
                            st.session_state.auth = {"logged_in": True, "user": u, "role": users[u]["role"]}
                            st.rerun()
                        else:
                            st.error("ข้อมูลไม่ถูกต้อง")
            with tab_s:
                with st.form("signup_f"):
                    new_u = st.text_input("ชื่อผู้ใช้ใหม่")
                    new_p = st.text_input("รหัสผ่านใหม่", type="password")
                    if st.form_submit_button("สมัครสมาชิก Member"):
                        if new_u in users:
                            st.error("ชื่อนี้มีคนใช้แล้ว")
                        elif new_u and new_p:
                            users[new_u] = {"pass": hash_password(new_p), "role": "member"}
                            save_users(users)
                            st.success("สมัครสำเร็จ! กรุณา Login")
    else:
        st.write(f"สวัสดี: **{st.session_state.auth['user']}** ({st.session_state.auth['role']})")
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.auth = {"logged_in": False, "user": "", "role": "guest"}
            st.session_state.cart = []
            st.rerun()

# --- 3. [FRONT-END] หน้าบ้าน (Public) ---
if choice == "🏠 หน้าบ้าน (Storefront)":
    # Header Layout
    h1, h2 = st.columns([1, 5])
    with h1:
        with st.container(border=True):
            if config["logo"] and Path(config["logo"]).exists():
                st.image(config["logo"])
            else:
                st.write("LOGO")
    with h2:
        st.title(config["shop_name"])

    st.divider()

    # Filter สินค้าที่แสดง (ไม่ซ่อน ไม่เก็บกรุ)
    visible_items = [i for i in db if not i.get("is_hidden") and not i.get("is_archived")]

    if not visible_items:
        st.info("ยังไม่มีสินค้าวางจำหน่าย")
    else:
        cols = st.columns(3)
        for idx, item in enumerate(visible_items):
            with cols[idx % 3]:
                with st.container(border=True):
                    if Path(item["image"]).exists(): st.image(item["image"])
                    st.subheader(item["name"])
                    st.write(f"ราคา: **{item['price']:,} บาท**")

                    # สิทธิ์การซื้อเฉพาะ Member และ Admin
                    if st.session_state.auth["logged_in"]:
                        if st.button(f"🛒 เพิ่มลงตะกร้า", key=f"buy_{idx}"):
                            st.session_state.cart.append(item)
                            st.toast(f"เพิ่ม {item['name']} แล้ว")
                    else:
                        st.caption("🔒 กรุณา Login เพื่อสั่งซื้อ")

    # ส่วนของตะกร้า (ถ้ามีการเลือกสินค้า)
    if st.session_state.cart:
        with st.expander("📋 รายการสั่งซื้อของคุณ", expanded=True):
            total = sum(i["price"] for i in st.session_state.cart)
            st.table(pd.DataFrame(st.session_state.cart)[["name", "price"]])
            st.subheader(f"รวมทั้งสิ้น: {total:,} บาท")
            if st.button("✅ ยืนยันการสั่งซื้อ"):
                st.balloons()
                st.success("ส่งรายการสั่งซื้อให้ James เรียบร้อย!")
                st.session_state.cart = []

# --- 4. [BACK-END] หลังบ้าน (Admin Only) ---
elif choice == "⚙️ หลังบ้าน (Admin Panel)":
    st.title("⚙️ จัดการคลังสินค้า")
    with st.expander("➕ เพิ่มสินค้าใหม่"):
        with st.form("add_p", clear_on_submit=True):
            n = st.text_input("ชื่อสินค้า")
            p = st.number_input("ราคา", min_value=0.0)
            img = st.file_uploader("รูปภาพ", type=['png', 'jpg', 'jpeg'])
            if st.form_submit_button("บันทึก"):
                if n and img:
                    path = IMG_DIR / img.name
                    with open(path, "wb") as f: f.write(img.getbuffer())
                    db.append({"name": n, "price": p, "image": str(path), "is_hidden": False})
                    save_db(db);
                    st.rerun()

    st.divider()
    for idx, item in enumerate(db):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                st.image(item["image"])
            with c2:
                un = st.text_input("ชื่อ", item["name"], key=f"un_{idx}")
                up = st.number_input("ราคา", value=float(item["price"]), key=f"up_{idx}")
                uh = st.checkbox("ซ่อนหน้าบ้าน", value=item.get("is_hidden"), key=f"uh_{idx}")
            with c3:
                if st.button("💾 บันทึก", key=f"sv_{idx}"):
                    db[idx].update({"name": un, "price": up, "is_hidden": uh})
                    save_db(db);
                    st.rerun()
                if st.button("🗑️ ลบ", key=f"dl_{idx}"):
                    del db[idx];
                    save_db(db);
                    st.rerun()

# --- 5. [USER MGMT] จัดการสมาชิก (Admin Only) ---
elif choice == "👥 จัดการสมาชิก/Admin":
    st.title("👥 จัดการผู้ใช้งาน")

    # ส่วนเพิ่ม Admin โดย Admin
    with st.expander("➕ เพิ่มผู้ใช้งานใหม่ (ระบุสิทธิ์ได้)"):
        with st.form("admin_add_user"):
            ad_u = st.text_input("Username")
            ad_p = st.text_input("Password", type="password")
            ad_r = st.selectbox("Role", ["member", "admin"])
            if st.form_submit_button("สร้างบัญชี"):
                if ad_u and ad_p:
                    users[ad_u] = {"pass": hash_password(ad_p), "role": ad_r}
                    save_users(users);
                    st.success(f"สร้าง {ad_u} เป็น {ad_r} แล้ว");
                    st.rerun()

    st.divider()
    # ตารางแสดงรายชื่อสมาชิกทั้งหมด
    st.subheader("รายชื่อผู้ใช้งานทั้งหมด")
    for u_name, u_info in list(users.items()):
        col1, col2, col3 = st.columns([2, 2, 1])
        col1.write(f"👤 {u_name}")
        col2.write(f"สิทธิ์: `{u_info['role']}`")
        if u_name != "admin":  # ป้องกันการลบ Admin หลัก
            if col3.button("ลบ", key=f"del_user_{u_name}"):
                del users[u_name]
                save_users(users);
                st.rerun()
