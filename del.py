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
                    st.error("❌ Invalid username or password.")

    elif selected == "Register":
        st.subheader("📝 Create a new account")
        with st.form("register_form"):
            username = st.text_input("👤 Choose a Username")
            password = st.text_input("🔐 Choose a Password", type="password")
            role = st.selectbox("🎭 Select Role", [
                "Student", "Homeroom Teacher", "Subject Teacher", "Vice Principal", "Principal"
            ])
            submitted = st.form_submit_button("Register")
            if submitted:
                register_user(username, password, role)

if __name__ == "__main__":
    main()