import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Auth + Chatbot", layout="centered")


# -----------------------------------------------------------
# SESSION VARIABLES
# -----------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "token" not in st.session_state:
    st.session_state.token = None

if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None



# -----------------------------------------------------------
# SIDEBAR MENU
# -----------------------------------------------------------
if not st.session_state.logged_in:
    menu = st.sidebar.selectbox(
        "Menu",
        ["Register", "Login", "Forgot Password"]
    )
else:
    menu = st.sidebar.selectbox(
        "Dashboard",
        ["Chatbot", "Logout"]
    )



# -----------------------------------------------------------
# REGISTER
# -----------------------------------------------------------
if menu == "Register":
    st.header("Create an Account")

    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        res = requests.post(
            f"{BASE_URL}/register",
            json={"email": email, "username": username, "password": password}
        )

        try:
            data = res.json()
            if res.status_code == 200:
                st.success("Registration Successful!")
            else:
                st.error(data.get("detail", "Error"))
        except:
            st.error("Server Error!")



# -----------------------------------------------------------
# LOGIN
# -----------------------------------------------------------
elif menu == "Login":
    st.header("Login to Your Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(
            f"{BASE_URL}/login",
            json={"email": email, "password": password}
        )

        data = res.json()

        if res.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.token = data["token"]
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error(data.get("detail", "Invalid Credentials"))



# -----------------------------------------------------------
# FORGOT PASSWORD
# -----------------------------------------------------------
elif menu == "Forgot Password":
    st.header("Reset Your Password")

    email = st.text_input("Enter Registered Email")

    if st.button("Send OTP"):
        res = requests.post(f"{BASE_URL}/forgot-password", params={"email": email})

        if res.status_code == 200:
            st.success("OTP sent to your email!")
        else:
            st.error(res.json().get("detail", "Error sending OTP"))

    otp = st.text_input("Enter OTP")
    new_password = st.text_input("Enter New Password", type="password")

    if st.button("Reset Password"):
        res = requests.post(
            f"{BASE_URL}/set-new-password",
            params={"email": email, "new_password": new_password}
        )

        if res.status_code == 200:
            st.success("Password reset successfully!")
        else:
            st.error(res.json().get("detail", "Error resetting password"))



# -----------------------------------------------------------
# LOGOUT
# -----------------------------------------------------------
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.token = None
    st.success("Logged out successfully!")
    st.rerun()



# -----------------------------------------------------------
# CHATBOT SECTION
# -----------------------------------------------------------
elif menu == "Chatbot":
    st.header("📘 PDF Based Smart Chatbot")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        st.session_state.pdf_file = uploaded_file
        st.success("PDF Uploaded Successfully!")

        # Upload PDF to backend immediately
        files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
        requests.post(f"{BASE_URL}/upload_pdf", files=files)

    question = st.text_input("Ask any question from your PDF")

    if st.button("Ask"):
        if st.session_state.pdf_file is None:
            st.error("Please upload a PDF first!")
        else:
            res = requests.get(
    f"{BASE_URL}/ask",
    params={"q": question}
)


            data = res.json()
            answer = data.get("answer", "No answer")

            st.write("### 🧠 Answer:")
            st.success(answer)

