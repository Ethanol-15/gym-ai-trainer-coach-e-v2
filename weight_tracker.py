import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
from supabase import create_client

# connect to supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_weight(user_id, log_date, weight):
    try:
        existing = supabase.table("weight_logs")\
            .select("weight")\
            .eq("user_id", user_id)\
            .eq("log_date", str(log_date))\
            .execute()

        if existing.data and existing.data[0]["weight"] == weight:
            st.warning("⚠️ This exact entry already exists for this date. No changes made.")
            return

        supabase.table("weight_logs").upsert({
            "user_id": user_id,
            "log_date": str(log_date),
            "weight": weight
        }).execute()

    except Exception as e:
        st.error(f"Error saving weight: {e}")


def update_weight(user_id, log_date, new_weight):
    # Updates an existing weight log entry by date
    try:
        supabase.table("weight_logs")\
            .update({"weight": new_weight})\
            .eq("user_id", user_id)\
            .eq("log_date", str(log_date))\
            .execute()
    except Exception as e:
        st.error(f"Error updating weight: {e}")


def load_weight_logs(user_id):
    try:
        result = supabase.table("weight_logs")\
            .select("log_date, weight")\
            .eq("user_id", user_id)\
            .order("log_date", desc=False)\
            .execute()

        if not result.data:
            return pd.DataFrame(columns=["log_date", "weight"])

        df = pd.DataFrame(result.data)
        df["log_date"] = pd.to_datetime(df["log_date"])
        return df

    except Exception as e:
        st.error(f"Error loading weight logs: {e}")
        return pd.DataFrame(columns=["log_date", "weight"])


def render_weight_tracker():

    if st.button("⬅ Back to Coach Chat"):
        st.session_state["page"] = "chat"
        st.rerun()

    user = st.session_state.get("user")

    st.markdown("## Weight Tracker")

    if not user:
        st.warning("Please login to use the weight tracker.")
        return

    user_id = user["id"]

    # --- CAREFUL NOTICE ---
    st.info(
        "⚠️ **Be careful when logging your weight.** "
        "Logs are not fully editable — you can only correct an existing date's entry. "
        "Double-check your date and weight before saving."
    )

    # --- LOG FORM ---
    with st.form("weight_form"):
        log_date = st.date_input("Date", value=date.today())
        weight = st.number_input(
            "Weight (kg)",
            min_value=20.0,
            max_value=300.0,
            step=0.1
        )
        submitted = st.form_submit_button("Save Weight")

        if submitted:
            save_weight(user_id, log_date, weight)
            st.success("Weight saved!")

    # --- LOAD LOGS ---
    df = load_weight_logs(user_id)

    if df.empty:
        st.info("No weight logs yet. Add your first entry.")
        return

    # --- EDIT SECTION ---
    st.markdown("### Edit a Log Entry")
    st.caption("Made a mistake? Select the date of the entry you want to correct.")

    edit_dates = df["log_date"].dt.date.tolist()
    selected_edit_date = st.selectbox("Select date to edit", edit_dates)

    existing_row = df[df["log_date"].dt.date == selected_edit_date]
    existing_weight = float(existing_row["weight"].values[0]) if not existing_row.empty else 0.0

    with st.form("edit_weight_form"):
        st.markdown(f"**Current weight on {selected_edit_date}:** {existing_weight} kg")
        new_weight = st.number_input(
            "New Weight (kg)",
            min_value=20.0,
            max_value=300.0,
            step=0.1,
            value=existing_weight
        )
        edit_submitted = st.form_submit_button("Update Entry")

        if edit_submitted:
            if new_weight == existing_weight:
                st.warning("⚠️ New weight is the same as the existing entry. No changes made.")
            else:
                update_weight(user_id, selected_edit_date, new_weight)
                st.success(f"Entry for {selected_edit_date} updated to {new_weight} kg!")
                st.rerun()

    # --- PROGRESS CHART ---
    st.markdown("### Progress Chart")

    min_weight = df["weight"].min()
    max_weight = df["weight"].max()

    if min_weight == max_weight:
        y_min = min_weight - 5
        y_max = max_weight + 5
    else:
        y_min = min_weight - 2
        y_max = max_weight + 2

    fig = px.line(
        df,
        x="log_date",
        y="weight",
        markers=True,
        title="Weight Progress"
    )
    fig.update_layout(
        height=400,
        margin=dict(l=70, r=30, t=60, b=60),
        yaxis=dict(title="Weight (kg)", range=[y_min, y_max]),
        xaxis=dict(title="Date")
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- ANALYTICS ---
    start_weight = df["weight"].iloc[0]
    current_weight = df["weight"].iloc[-1]
    total_change = current_weight - start_weight
    highest_weight = df["weight"].max()
    lowest_weight = df["weight"].min()

    st.markdown("### Analytics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Start Weight", f"{start_weight:.1f} kg")
    col2.metric("Current Weight", f"{current_weight:.1f} kg")
    col3.metric("Total Change", f"{total_change:+.1f} kg")

    col4, col5 = st.columns(2)
    col4.metric("Highest Weight", f"{highest_weight:.1f} kg")
    col5.metric("Lowest Weight", f"{lowest_weight:.1f} kg")

    if len(df) >= 2:
        df["daily_change"] = df["weight"].diff()
        avg_change = df["daily_change"].mean()

        if avg_change <= -0.30:
            trend = "Extreme Weight Loss ⚠️"
        elif avg_change <= -0.15:
            trend = "Fast Weight Loss"
        elif avg_change <= -0.05:
            trend = "Mild Weight Loss"
        elif -0.05 < avg_change < 0.05:
            trend = "Maintaining Weight"
        elif 0.05 <= avg_change < 0.15:
            trend = "Mild Weight Gain"
        elif 0.15 <= avg_change < 0.30:
            trend = "Fast Weight Gain"
        else:
            trend = "Extreme Weight Gain ⚠️"

        st.metric("Trend", trend)
