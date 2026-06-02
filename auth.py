# ============================================
# auth.py — Database + Authentication
# Coach E Gym App
# ============================================
# MIGRATION: SQLite → Supabase
#
# WHAT CHANGED:
#   - No more sqlite3 import
#   - No more local users.db file
#   - All DB operations now go through Supabase
#   - Everything else stays the same:
#     same functions, same return values,
#     same logic — just different DB connection
#
# HOW SUPABASE WORKS vs SQLite:
#   SQLite:   c.execute("SELECT * FROM users WHERE email = ?", (email,))
#   Supabase: supabase.table("users").select("*").eq("email", email).execute()
#
# The pattern is always:
#   supabase.table("table_name").action().filter().execute()
# ============================================

import bcrypt
import streamlit as st
from supabase import create_client

# ============================================
# SUPABASE CONNECTION
# ============================================

# reads from .streamlit/secrets.toml
# same way GROQ_API_KEY is read
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# create the supabase client
# this is the replacement for sqlite3.connect()
# one client handles all DB operations
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================
# INIT DB — no longer needed but kept
# so app.py doesn't need changes
# ============================================

def init_db():
    # tables are already created in Supabase dashboard
    # this function now does nothing
    # kept so app.py call to auth.init_db() doesn't crash
    pass


# ============================================
# PASSWORD FUNCTIONS (unchanged)
# bcrypt works exactly the same
# ============================================

def hash_password(password):
    # converts plain text to secure hash
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def check_password(entered_password, stored_hash):
    # compares entered password against stored hash
    return bcrypt.checkpw(
        entered_password.encode(),
        stored_hash.encode()
    )


# ============================================
# USER FUNCTIONS
# ============================================

def register_user(email, password):
    # ----------------------------------------
    # Adds a new user to Supabase users table
    #
    # Returns True if success
    # Returns False if email already exists
    # ----------------------------------------
    try:
        hashed = hash_password(password)

        # INSERT into users table
        # .insert() takes a dict of column: value
        supabase.table("users").insert({
            "email": email,
            "password": hashed
        }).execute()

        return True

    except Exception as e:
        # duplicate email causes an exception
        # same as sqlite3.IntegrityError before
        print(f"Register error: {e}")
        return False


def login_user(email, password):
    # ----------------------------------------
    # Checks email + password against Supabase
    #
    # Returns dict {"id": ..., "email": ...}
    # Returns None if wrong credentials
    # ----------------------------------------
    try:
        # SELECT id, password FROM users WHERE email = ?
        result = supabase.table("users")\
            .select("id, password")\
            .eq("email", email)\
            .execute()

        # result.data is a list of matching rows
        # if empty — email not found
        if not result.data:
            return None

        user = result.data[0]

        # check if password matches stored hash
        if check_password(password, user["password"]):
            return {
                "id": user["id"],
                "email": email
            }

        return None

    except Exception as e:
        print(f"Login error: {e}")
        return None


# ============================================
# CONVERSATION FUNCTIONS
# ============================================

def create_conversation(user_id, title):
    # ----------------------------------------
    # Creates a new conversation in Supabase
    # Returns the new conversation's id
    #
    # Called in app.py when:
    #   - user sends first message of new chat
    #   - user clicks New Chat button
    # ----------------------------------------
    try:
        result = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": title
        }).execute()

        # result.data[0] is the inserted row
        # including the auto-generated id
        return result.data[0]["id"]

    except Exception as e:
        print(f"Create conversation error: {e}")
        return None


def get_conversations(user_id):
    # ----------------------------------------
    # Returns all conversations for a user
    # Newest first for sidebar display
    # ----------------------------------------
    try:
        result = supabase.table("conversations")\
            .select("id, title, created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()

        return result.data

    except Exception as e:
        print(f"Get conversations error: {e}")
        return []


def load_conversation_messages(conversation_id):
    # ----------------------------------------
    # Loads all messages for ONE conversation
    # Called when user clicks a past chat
    # Returns list of dicts matching
    # st.session_state.messages format
    # ----------------------------------------
    try:
        result = supabase.table("messages")\
            .select("role, content")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=False)\
            .execute()

        return result.data

    except Exception as e:
        print(f"Load messages error: {e}")
        return []


# ============================================
# MESSAGE FUNCTIONS
# ============================================

def save_message(user_id, conversation_id, role, content):
    # ----------------------------------------
    # Saves ONE message to Supabase
    # Called twice per chat exchange:
    #   save_message(..., "user", prompt)
    #   save_message(..., "assistant", answer)
    # ----------------------------------------
    try:
        supabase.table("messages").insert({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content
        }).execute()

    except Exception as e:
        print(f"Save message error: {e}")


def load_messages(user_id):
    # ----------------------------------------
    # Loads most recent conversation on login
    # Kept for backwards compatibility
    # ----------------------------------------
    try:
        # get most recent conversation
        result = supabase.table("conversations")\
            .select("id")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()

        if not result.data:
            return []

        conversation_id = result.data[0]["id"]
        return load_conversation_messages(conversation_id)

    except Exception as e:
        print(f"Load messages error: {e}")
        return []


def clear_messages(user_id):
    # ----------------------------------------
    # Deletes all messages for a user
    # For future "Clear History" button
    # ----------------------------------------
    try:
        supabase.table("messages")\
            .delete()\
            .eq("user_id", user_id)\
            .execute()

    except Exception as e:
        print(f"Clear messages error: {e}")


def delete_conversation(user_id, conversation_id):
    try:
        # delete all messages inside the conversation first
        supabase.table("messages")\
            .delete()\
            .eq("user_id", user_id)\
            .eq("conversation_id", conversation_id)\
            .execute()

        # then delete the conversation itself
        supabase.table("conversations")\
            .delete()\
            .eq("user_id", user_id)\
            .eq("id", conversation_id)\
            .execute()

    except Exception as e:
        print(f"Delete conversation error: {e}")