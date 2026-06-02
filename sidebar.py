import streamlit as st
import auth_ui
import auth 

# fucntion that makes users sign up or log in before te 5 free chats are used
def show_save_nudge():

    # heck if the user is already logged in
    # if logged in stop the function
    if st.session_state.get("user") is not None:
        return

    # get the chat from the session state,
    # if there are no mesages yet use empty list
    messages = st.session_state.get("messages", [])

    # if the guest already has 4 or more messages,
    # show a warning the chat may be lost on refresh
    if len(messages) >= 4:
        st.warning(
            "⚠️ Your conversation will be lost on refresh. "
            "**Sign up** in the sidebar to save your chat history!",
        )

#  render the sidebar
def render():
    with st.sidebar:

        # app title and short discription
        st.markdown("## Coach E")
        st.markdown("*Your AI-powered gym coach*")
        st.divider()
        # show the weight tracker
        _render_progress_tracker_menu()
        st.divider()
        # show the convo history
        _render_conversation_history()
        st.divider()
        # show the profile
        _render_profile()
        st.divider()
        # show the dev info 
        _render_footer()

# reassuring the user if they want to delete a conversation
@st.dialog("Delete conversation?")
def delete_conversation_modal(user_id, conversation_id):
    st.warning("Are you sure you want to delete this conversation?")
    st.markdown("This action cannot be undone.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, delete", use_container_width=True, key="confirm_delete"):
            auth.delete_conversation(user_id, conversation_id)

            if st.session_state.get("conversation_id") == conversation_id:
                st.session_state["messages"] = []
                st.session_state["conversation_id"] = None
                st.session_state["page"] = "chat"

            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True, key="cancel_delete"):
            st.rerun()
            
# this functions is the render conversation history
def _render_conversation_history():
    user = st.session_state.get("user")
 
    # only show for logged in users
    if user is None:
        return
 
    st.markdown("####Conversations")
 
    # New Chat button — starts a fresh conversation
    # sets conversation_id to None so app.py knows
    # to create a new one on next message
    if st.button("➕ New Chat", use_container_width=True, key="new_chat_btn"):
        st.session_state["messages"] = []
        st.session_state["conversation_id"] = None
        st.session_state["page"] = "chat"
        st.rerun()
 
    # load all past conversations for this user
    conversations = auth.get_conversations(user["id"])
 
    if not conversations:
        st.caption("No conversations yet.")
        return
 
    # show each conversation as a clickable button
    # title is the first 40 chars of first message
    for convo in conversations:
        # truncate long titles so they fit in sidebar
        title = convo["title"]
        if len(title) > 35:
            title = title[:35] + "..."
 
        # highlight the currently active conversation
        # so user knows which one they are in
        is_active = (
            st.session_state.get("conversation_id") == convo["id"]
        )
 
        # add a marker if this is the active conversation
        button_label = f"{'▶ ' if is_active else ''}{title}"

        # create 2 columns
        # left = open convo
        # right delete convo
        col1, col2 = st.columns ([5,1])

        with col1:
            if st.button(button_label, use_container_width=True, key=f"convo_{convo['id']}"):
                # load messages for this conversation
                st.session_state["messages"] = auth.load_conversation_messages(convo["id"])
                # set active conversation id
                st.session_state["conversation_id"] = convo["id"]
                st.session_state["page"] = "chat"
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_convo_{convo['id']}"):
                delete_conversation_modal(user["id"], convo["id"])
 
# this function shwows the user profile area in side bar
def _render_profile():

    # get the logged -in user from session state
    user = st.session_state.get("user")

    # if no users show guest mode
    if user is None:
        st.markdown("#### Guest Mode")
        st.markdown("You can try Coach E for free.")

        # get how many chats has been used in guest mode
        guest_chat_count = st.session_state.get("guest_chat_count", 0)

        # set free chat limit for the guest
        #a adn calculates the remaining free chats
        free_chat_limit = 5
        remaining = max(0, free_chat_limit - guest_chat_count)

        # display the remaining free chats
        st.info(f"💬 Free chats left: {remaining}")
        st.markdown("Sign up or login to continue after your free chats.")

        # if the user clicks login, open the modal from auth.ui
        if st.button("Login", use_container_width=True, key="sidebar_login_btn"):
            auth_ui.login_modal()

        # if the user clicks sign up, open the modal from auth.ui
        if st.button("Sign Up", use_container_width=True, key="sidebar_signup_btn"):
            auth_ui.signup_modal()

        return

    # showing user profile
    st.markdown("#### Your Account")
    st.markdown("✅ Logged in as:")
    st.markdown(f"**{user['email']}**")

    # logout button
    if st.button("Logout", use_container_width=True, key="logout_btn"):
        # remove the logged in user
        st.session_state["user"] = None
        st.query_params.clear()
        # clear chat messages for the next user or guest
        st.session_state["messages"] = []
        # reset guest chat count to 0
        st.session_state["guest_chat_count"] = 0
        st.session_state["conversation_id"] = None
        # send usee to the chatbot page
        st.session_state["page"] = "chat"
        # refresh the app so changes takes effect
        st.rerun()

# render the weight tracker for logged in users
def _render_progress_tracker_menu():
    user = st.session_state.get("user")

    st.markdown("#### Progress Tracker")
    # if user isnt logged it wont open
    if user is None:
        st.caption("Login to unlock progress tracking.")
        return
    
    # if user is logged in, weight tracker will open
    if st.button("Open Weight Tracker", use_container_width=True):
        # opens the weight tracker page
        st.session_state["page"] = "weight_tracker"
        st.rerun()

    # if user is logged in, strength tracker will open
    if st.button("Open Strength Tracker", use_container_width=True):
        # opens the strength tracker page
        st.session_state["page"] = "strength_tracker"
        st.rerun()

    # if user is logged in, calorie tracker will open
    if st.button("Open Calorie Tracker", use_container_width=True):
        # opens the strength tracker page
        st.session_state["page"] = "calorie_tracker"
        st.rerun()

# footer 
def _render_footer():
    st.markdown("#### About the Developer")
    st.markdown("Built by **Ethan Lyle Cruz**")
    st.markdown("[Portfolio](https://ethancruz-portfolio.vercel.app)")
    st.markdown("[LinkedIn](https://www.linkedin.com/in/ethan-cruz-992730337/)")
    st.markdown("[Contact Me](mailto:cruz.ethanlyle2003@gmail.com)")

    st.markdown(" ")
    st.caption("Coach E v2 — Powered by LLaMA 3.3 + RAG")
