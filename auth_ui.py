
# auth_ui,py login and sign up modal popups
# when the user sign in or login in tha sidebar the pop up modals will be displayed
import streamlit as st
import auth

# free chat limit must be 5 
FREE_CHAT_LIMIT = 5

# login modal
@st.dialog("Login")
def login_modal():

    # greeting
    st.markdown("#### Welcome back 👋")

    # email and password input fields
    login_email = st.text_input("Email", key="modal_login_email", placeholder="you@email.com")
    login_password = st.text_input("Password", type="password", key="modal_login_password", placeholder="Your password")

    # loggin button
    if st.button("Login", use_container_width=True, key="modal_login_btn"):

        # validation if the fields are not empty before going to the database
        if not login_email or not login_password: 
            st.error("Please fill in all fields.")
        else:
            user = auth.login_user(login_email, login_password)

            # load the user chat history messages and has unlimited chat
            if user:
                st.session_state["user"] = user
                st.session_state["guest_chat_count"] = 0
                
                # laod most recent conversations newest first
                conversations = auth.get_conversations(user["id"])
                if conversations:
                     # load the most recent conversation
                    most_recent = conversations[0]
                    st.session_state["conversation_id"] = most_recent["id"]
                    st.session_state["messages"] = auth.load_conversation_messages(most_recent["id"])
                else:
                    # no conversations yet — fresh start
                    st.session_state["conversation_id"] = None
                    st.session_state["messages"] = []

                st.session_state["user"] = user
                st.query_params["user_id"] = str(user["id"])
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Wrong email or password.")

# sig up modal
@st.dialog("Sign Up")
def signup_modal():
    st.markdown("#### Create your account 💪")

    # sign up input fields
    signup_email = st.text_input("Email", key="modal_signup_email", placeholder="you@email.com")
    signup_password = st.text_input("Password", type="password", key="modal_signup_password", placeholder="Choose a password")
    signup_password_confirm = st.text_input("Confirm Password", type="password", key="modal_signup_confirm", placeholder="Repeat your password")

    # Sign in button
    if st.button("Create Account", use_container_width=True, key="modal_signup_btn"):
        if not signup_email or not signup_password or not signup_password_confirm:
            st.error("Please fill in all fields.")
        elif signup_password != signup_password_confirm:
            st.error("Passwords don't match.")
        elif len(signup_password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            success = auth.register_user(signup_email, signup_password)

            if success:
                # automatically log them in right after signing up
                user = auth.login_user(signup_email, signup_password)

                if user:
                    st.session_state["user"] = user
                    st.session_state["guest_chat_count"] = 0
                    # no conversations yet since brand new account
                    st.session_state["conversation_id"] = None
                    st.session_state["messages"] = []
                    st.success("Account created! Welcome to Coach E 💪")
                    st.rerun()
            else:
                st.error("Email already registered.")

# initializing auth state
def init_auth_state():

    # if no user key exist, its guest so it is set to none, nobody logged in
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # if no guest count exist yet it is set to 0 it means 0 chat has been used
    if "guest_chat_count" not in st.session_state:
        st.session_state.guest_chat_count = 0
