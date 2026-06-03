import streamlit as st
from groq import Groq
from groq import RateLimitError #put this inorder that shows groq is overloaded
from rag import find_relevant_entries
import os 
import auth
import sidebar
from prompts import SYSTEM_PROMPT
import time
import weight_tracker
import strength_tracker
import calorie_tracker

# page config
st.set_page_config(
    page_title = "Coach E — Your Gym Coach",
    page_icon  = "🏋️",
    layout     = "centered",
    initial_sidebar_state="expanded"
)

#inistalizing the database SQLite
auth.init_db() 

# initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "guest_chat_count" not in st.session_state:
    st.session_state.guest_chat_count = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "chat"
if "conversation_id" not in st.session_state:       # none means no conversation yet, gets set when first mesage is set
    st.session_state.conversation_id = None

# restore user from URL after browser refresh
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None


# sidebar
sidebar.render()

# get the current user and login status
user = st.session_state.get("user")
is_logged_in = user is not None
FREE_CHAT_LIMIT = 5

# page routing for users and guest
current_page = st.session_state.get("page", "chat")
if current_page == "weight_tracker":

    # guest users are redirected back to chat
    if not is_logged_in:
        st.session_state["page"] = "chat"
        st.warning("Please login or sign up to use the Weight Tracker.")
        st.rerun()
    
    # logged in users can access the weight tracker
    else:
        weight_tracker.render_weight_tracker()
        # stop the chatbot page from rendering underneath
        st.stop()

if current_page == "strength_tracker":

    # guest users are redirected back to chat
    if not is_logged_in:
        st.session_state["page"] = "chat"
        st.warning("Please login or sign up to use the Strength Tracker.")
        st.rerun()
    # logged in users can access the weight tracker
    else:
        strength_tracker.render_strength_tracker()
        # stop the chatbot page from rendering underneath
        st.stop()

if current_page == "calorie_tracker":

    # guest users are redirected back to chat
    if not is_logged_in:
        st.session_state["page"] = "chat"
        st.warning("Please login or sign up to use the Strength Tracker.")
        st.rerun()
    # logged in users can access the weight tracker
    else:
        calorie_tracker.render_calorie_tracker()
        # stop the chatbot page from rendering underneath
        st.stop()


# groq API key
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

client = Groq(api_key=GROQ_API_KEY)

# MODEL SETTINGS
DEV_MODE = False
MODEL = (
    "llama-3.1-8b-instant"
    if DEV_MODE
    else "llama-3.3-70b-versatile"
)
MAX_TOKENS = 250 if DEV_MODE else 500

# app title
# custom CSS for Gemini dark style
st.markdown("""
<style>
    /* dark background */
    .stApp {
        background-color: #0d0d0d;
    }
    /* hide default header */
    header {visibility: hidden;}
    
    /* center the greeting */
    .greeting {
        text-align: center;
        padding: 20vh 0 2rem 0;
        font-size: 2rem;
        font-weight: 600;
        color: white;
    }
    /* gradient text for Coach E */
    .gradient-text {
        background: linear-gradient(
            135deg, #4285f4, #ea4335, #fbbc04, #34a853
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    /* clean input bar */
    .stChatInput input {
        background-color: #1e1e1e !important;
        border-radius: 24px !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
    /* chat messages */
    .stChatMessage {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# show greeting only when no messages yet
if not st.session_state.get("messages", []):

    # this part the username will show in the greeting 
    user = st.session_state.get("user")
    if user:
        user_email = user["email"]
        username = user_email.split("@")[0].capitalize()
        greeting_text = f"What can I help with, {username}?"
    else:
        greeting_text = "What can I help with, Bro?"
    st.markdown(f"""
    <div class="greeting">
        <span class="gradient-text">✦</span><br>
        {greeting_text}
    </div>
    """, unsafe_allow_html=True)

# display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# chat input
if prompt := st.chat_input("Ask Coach E anything..."):

    # rate limit check - 2 secodn coldown if user is spamming
    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0
    if time.time() - st.session_state.last_request_time < 2:
        st.warning("Please wait before sending another message.")
        st.stop()
    st.session_state.last_request_time = time.time()


    # CHECK FREE CHAT LIMIT
    if not is_logged_in and st.session_state.guest_chat_count >= FREE_CHAT_LIMIT:
        st.warning("You have used your 5 free chats. Please login or sign up to continue using Coach E.")
        st.stop()

    # Count guest messages only if not logged in
    if not is_logged_in:
        st.session_state.guest_chat_count += 1

    # create a new conbversation if none is active
    # new chat button in side bar
    # the title is the fiurst 40 chars of the first message
    if is_logged_in and st.session_state.get("conversation_id") is None:
        title = prompt[:40]
        conversation_id = auth.create_conversation(user["id"], title)
        st.session_state["conversation_id"] = conversation_id

    # display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # add to session state history
    st.session_state.messages.append({
        "role":    "user",
        "content": prompt
    })
    # save_message now needs conversation_id
    if is_logged_in:
        auth.save_message(
            user["id"], 
            st.session_state["conversation_id"],
            "user", 
            prompt
        )

    # RAG search
    # find relevant entries from your dataset for dev k=1
    relevant_entries = find_relevant_entries(prompt, top_k=1)

    # build RAG context
    rag_context = "Relevant examples from knowledge base:\n\n"
    for entry in relevant_entries:
        rag_context += f"Q: {entry['instruction']}\n"
        rag_context += f"A: {entry['output']}\n\n"

    # combine system prompt + RAG
    full_system = SYSTEM_PROMPT  + "\n\n" + rag_context

    # build messages for Groq
    messages = [
        {
            "role":    "system",
            "content": full_system
        }
    ]

    # add conversation history
    for msg in st.session_state.messages[:-1]:
        messages.append({
            "role":    msg["role"],
            "content": msg["content"]
        })

    # limit to last 10 messages so 12 but for dev 8
    # keeps system prompt always at position 0
    # limit to last 6 messages in dev mode
    if len(messages) > 8:
        system_msg  = messages[0]
        recent_msgs = messages[-6:]
        messages    = [system_msg] + recent_msgs

    # add current question
    messages.append({
        "role":    "user",
        "content": prompt
    })

    # get response from Groq
    with st.chat_message("assistant"):
        with st.spinner("Coach E is thinking..."):
            response = client.chat.completions.create(
                model = MODEL,
                messages    = messages,
                temperature = 0.3,
                max_tokens  = MAX_TOKENS
            )
            answer = response.choices[0].message.content
            st.markdown(answer)

    # add response to ession state
    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer
    })

    if is_logged_in:
       auth.save_message(user["id"], st.session_state["conversation_id"], "assistant", answer)
