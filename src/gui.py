import streamlit as st
import httpx

# FastAPI backend URL
BASE_URL = "http://localhost:8000"  # Update this to match your FastAPI server's URL


# Helper function to set cookies
def set_cookie(cookie_name, cookie_value):
    st.session_state[cookie_name] = cookie_value


# Helper function to get cookies
def get_cookie(cookie_name):
    return st.session_state.get(cookie_name, None)


# Helper function to clear all cookies
def clear_cookies():
    if "validated_username" in st.session_state:
        del st.session_state["validated_username"]
    if "show_chat_button" in st.session_state:
        del st.session_state["show_chat_button"]


# Check if the user is logged in
def is_logged_in():
    return get_cookie("validated_username") is not None


# User Login function
def user_login():
    st.title("👋 Welcome Back!")
    st.write("Let's get you logged in.")

    username = st.text_input("Username", placeholder="Type your username here")
    password = st.text_input(
        "Password", type="password", placeholder="Type your password here"
    )

    if st.button("Login"):
        with st.spinner("Hang tight... Logging you in!"):
            try:
                response = httpx.post(
                    f"{BASE_URL}/login",
                    json={"username": username, "password": password},
                    timeout=30.0,
                )

                if response.status_code == 202:
                    st.success(f"Welcome aboard, {username}!")
                    set_cookie("validated_username", username)
                    st.session_state["show_chat_button"] = True
                else:
                    st.error(
                        "Oops! Those details don't seem right. Give it another shot."
                    )
            except httpx.ReadTimeout:
                st.error("The server's taking a bit too long. Try again in a moment!")

    # Display "Go to Chat" button if login was successful
    if st.session_state.get("show_chat_button", False):
        if st.button("Go to Chat"):
            st.session_state["page"] = "Chat"  # Switch to Chat page


# Chat function
def chat():
    st.title("💬 Chat with Us!")
    st.write("Ask us anything, we're here to help.")

    query = st.text_input("Your message", placeholder="Type something...")

    if st.button("Send"):
        validated_username = get_cookie("validated_username")
        if validated_username is None:
            st.warning("You need to log in first.")
            return

        with st.spinner("Getting your response..."):
            try:
                response = httpx.post(
                    f"{BASE_URL}/chat",
                    json={"student_query": query},
                    cookies={"validated_username": validated_username},
                    timeout=3000.0,
                )

                if response.status_code == 200:
                    result = response.json().get(
                        "response", "Hmm, no response available."
                    )
                    st.write(result)
                else:
                    st.error("Something went wrong on our end. We'll look into it.")
            except httpx.ReadTimeout:
                st.error("The server took too long to respond. Try again later.")


# Register function
def register_user():
    st.title("📝 Sign Up")
    st.write("Join us by creating a new account.")

    username = st.text_input("Choose a Username", placeholder="Pick a username")
    password = st.text_input(
        "Choose a Password", type="password", placeholder="Pick a secure password"
    )

    if st.button("Register"):
        with st.spinner("Creating your account..."):
            try:
                response = httpx.post(
                    f"{BASE_URL}/admin/add-student",
                    json={"username": username, "password": password},
                    timeout=3000.0,
                )

                if response.status_code == 201:
                    st.success(
                        f"Awesome, {username}! You're all set. You're logged in now."
                    )
                    set_cookie("validated_username", username)
                    st.session_state["show_chat_button"] = (
                        True  # Show chat button after registration
                    )
                else:
                    error_msg = response.json().get(
                        "detail", "Couldn't register you. Try again later."
                    )
                    st.error(error_msg)
            except httpx.ReadTimeout:
                st.error("Server took too long. Please try again in a bit.")

    # Display "Go to Chat" button if registration was successful
    if st.session_state.get("show_chat_button", False):
        if st.button("Go to Chat"):
            st.session_state["page"] = "Chat"  # Switch to Chat page


# View all registered users function
def view_registered_users():
    st.title("👥 Registered Users")
    st.write("Here's who has joined us so far:")

    with st.spinner("Loading..."):
        try:
            response = httpx.get(f"{BASE_URL}/admin/students", timeout=30.0)
            if response.status_code == 200:
                students = response.json().get("students", [])
                if students:
                    st.write("We have some cool people here:")
                    for student in students:
                        st.write(f"- {student['username']}")
                else:
                    st.info("Looks like no one's registered yet.")
            else:
                st.error("Couldn't fetch the users list. Try refreshing the page.")
        except httpx.ReadTimeout:
            st.error("Server response took too long. Try again shortly.")


# Log Out function
def log_out_user():
    st.title("🚪 Log Out")
    st.write("Leaving so soon?")

    # Check if the user is logged in before trying to log out
    validated_username = get_cookie("validated_username")
    if validated_username is None:
        st.warning("You are not logged in.")
        return

    if st.button("Log Out"):
        with st.spinner("Logging you out..."):
            try:
                # Optional: Call the backend API to log out
                response = httpx.delete(
                    f"{BASE_URL}/admin/delete-student/{validated_username}",
                    timeout=30.0,
                )

                if response.status_code == 200 or response.status_code == 404:
                    clear_cookies()
                    st.session_state["page"] = "Login"
                    st.success("You've been logged out. See you next time!")
                else:
                    st.error(response.json().get("detail", "Error logging out user."))
            except httpx.ReadTimeout:
                st.error("The server took too long to respond. Please try again.")


# Streamlit sidebar for navigation
st.sidebar.title("🌐 Navigation")

# Determine the page based on the login status
if "page" not in st.session_state:
    st.session_state["page"] = "Chat" if is_logged_in() else "Login"

# Set up navigation options based on login status
if is_logged_in():
    options = ["Chat", "View Registered Users", "Log Out"]
else:
    options = ["Register", "Login"]

# Safely set the selected page
if st.session_state["page"] not in options:
    st.session_state["page"] = options[0]  # Default to the first available option

choice = st.sidebar.radio(
    "Choose a section", options, index=options.index(st.session_state["page"])
)

# Update the current page in session state
st.session_state["page"] = choice

# Page routing
if choice == "Login":
    user_login()
elif choice == "Chat":
    chat()
elif choice == "Register":
    register_user()
elif choice == "View Registered Users":
    view_registered_users()
elif choice == "Log Out":
    log_out_user()
