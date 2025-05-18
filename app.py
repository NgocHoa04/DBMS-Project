import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# ------------------ Hàm login bằng user thật của MySQL ------------------
def login_user(username, password):
    DB_HOST = "localhost"
    DB_PORT = "3306"
    DB_NAME = "school_management"

    try:
        engine = create_engine(f"mysql+pymysql://{username}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        with engine.connect() as conn:
            role_mapping = {
                "student": "Student",
                "homeroom_teacher": "Homeroom Teacher",
                "subject_teacher": "Subject Teacher",
                "academic_coordinator": "Vice Principal",
                "admin_user": "Principal"
            }
            return role_mapping.get(username, "Unknown")
    except SQLAlchemyError:
        return None

# ------------------ Hàm xử lý hiển thị dashboard ------------------
def render_dashboard_by_role(role, username):
    st.success(f"✅ Logged in as **{username}** with role: **{role}**")
    st.write("---")

    if role == "Student":
        st.subheader("📚 Student Dashboard")
        st.write("Welcome to your student portal.")
    elif role == "Homeroom Teacher":
        st.subheader("👩‍🏫 Homeroom Teacher Dashboard")
    elif role == "Subject Teacher":
        st.subheader("📘 Subject Teacher Dashboard")
    elif role == "Vice Principal":
        st.subheader("🎓 Vice Principal Dashboard")
    elif role == "Principal":
        st.subheader("🏫 Principal Dashboard")
    else:
        st.error("⚠️ Unknown role. Please contact admin.")

    st.button("Logout", on_click=logout)

# ------------------ Logout ------------------
def logout():
    st.session_state.clear()
    st.rerun()

# ------------------ Main ------------------
def main():
    st.set_page_config(page_title="School Management System", layout="centered", page_icon="🏫")
    st.markdown("<h1 style='text-align: center; color: navy;'>🏫 School Management System</h1>", unsafe_allow_html=True)
    st.write("##")

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        render_dashboard_by_role(st.session_state["role"], st.session_state["username"])
        return

    selected = option_menu(
        menu_title=None,
        options=["Login", "Register"],
        icons=["box-arrow-in-right", "person-plus"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6"},
            "icon": {"color": "blue", "font-size": "18px"},
            "nav-link": {"font-size": "18px", "text-align": "center", "margin": "2px"},
            "nav-link-selected": {"background-color": "#3399ff", "color": "white"},
        }
    )

    if selected == "Login":
        st.subheader("🔐 Login to your account")
        with st.form("login_form"):
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                role = login_user(username, password)
                if role:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = role
                    st.rerun()
                else:
                    st.error("❌ Invalid MySQL username or password.")

    elif selected == "Register":
        st.subheader("📝 Create a new account")
        st.warning("⚠️ Việc đăng ký tài khoản mới hiện chưa được hỗ trợ. Vui lòng liên hệ quản trị viên để được cấp tài khoản.")

# ------------------ Run ------------------
if __name__ == "__main__":
    main()
