import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
from supabase import create_client

# connect to supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def calculate_estimated_strength(exercise_type, weight, bodyweight, reps):
    # Epley formula: load * (1 + reps / 30)
    # estimates one rep max based on reps and load
    if exercise_type == "Gym Exercise":
        load = weight
    elif exercise_type == "Calisthenics":
        load = bodyweight
    elif exercise_type == "Weighted Calisthenics":
        load = bodyweight + weight
    else:
        load = 0

    return load * (1 + reps / 30)


def save_strength_log(
    user_id,
    log_date,
    exercise_name,
    exercise_type,
    sets,
    reps,
    weight,
    bodyweight,
    estimated_strength
):
    # Saves one strength log entry to Supabase
    # uses user_id instead of user_email

    try:
        supabase.table("strength_logs").insert({
            "user_id": user_id,
            "log_date": str(log_date),
            "exercise_name": exercise_name,
            "exercise_type": exercise_type,
            "sets": sets,
            "reps": reps,
            "weight": weight,
            "bodyweight": bodyweight,
            "estimated_strength": estimated_strength
        }).execute()
    except Exception as e:
        st.error(f"Error saving strength log: {e}")


def load_strength_logs(user_id):
    # Loads all strength logs for the logged in user
    # Returns a pandas DataFrame for display and charting
    try:
        result = supabase.table("strength_logs")\
            .select("log_date, exercise_name, exercise_type, sets, reps, weight, bodyweight, estimated_strength")\
            .eq("user_id", user_id)\
            .order("log_date", desc=False)\
            .execute()

        if not result.data:
            return pd.DataFrame()

        df = pd.DataFrame(result.data)
        df["log_date"] = pd.to_datetime(df["log_date"])
        return df

    except Exception as e:
        st.error(f"Error loading strength logs: {e}")
        return pd.DataFrame()


def render_strength_tracker():

    # back button
    if st.button("⬅ Back to Coach E"):
        st.session_state["page"] = "chat"
        st.rerun()

    # get logged in user
    user = st.session_state.get("user")

    st.markdown("## Strength Tracker")

    # block guest users
    if not user:
        st.warning("Please login to use the strength tracker.")
        return

    # use user_id now instead of user_email
    user_id = user["id"]

    # exercise type selector — outside form so placeholder updates live
    exercise_type = st.selectbox(
        "Exercise Type",
        ["Gym Exercise", "Calisthenics", "Weighted Calisthenics"],
        key="exercise_type_select"
    )

    if exercise_type == "Gym Exercise":
        exercise_placeholder = "Example: Bench Press, Lat Pulldown, Leg Press"
    elif exercise_type == "Calisthenics":
        exercise_placeholder = "Example: Pull Up, Push Up, Dip"
    else:
        exercise_placeholder = "Example: Weighted Pull Up, Weighted Dip"

    with st.form("strength_form"):
        log_date = st.date_input("Date", value=date.today())

        exercise_name = st.text_input(
            "Exercise Name",
            placeholder=exercise_placeholder
        )

        sets = st.number_input("Sets", min_value=1, max_value=20, step=1)
        reps = st.number_input("Reps", min_value=1, max_value=100, step=1)

        # default values
        weight = 0.0
        bodyweight = 0.0

        if exercise_type == "Gym Exercise":
            weight = st.number_input(
                "Weight Used (kg)",
                min_value=0.0, max_value=500.0, step=0.5,
                key="gym_weight"
            )
        elif exercise_type == "Calisthenics":
            bodyweight = st.number_input(
                "Bodyweight (kg)",
                min_value=20.0, max_value=300.0, step=0.1,
                key="calisthenics_bodyweight"
            )
        elif exercise_type == "Weighted Calisthenics":
            bodyweight = st.number_input(
                "Bodyweight (kg)",
                min_value=20.0, max_value=300.0, step=0.1,
                key="weighted_bodyweight"
            )
            weight = st.number_input(
                "Added Weight (kg)",
                min_value=0.0, max_value=200.0, step=0.5,
                key="added_weight"
            )

        submitted = st.form_submit_button("Save Strength Log")

        if submitted:
            if not exercise_name:
                st.error("Please enter an exercise name.")
            else:
                estimated_strength = calculate_estimated_strength(
                    exercise_type, weight, bodyweight, reps
                )
                save_strength_log(
                    user_id, log_date, exercise_name,
                    exercise_type, sets, reps,
                    weight, bodyweight, estimated_strength
                )
                st.success("Strength log saved!")

    # load and display logs
    df = load_strength_logs(user_id)

    if df.empty:
        st.info("No strength logs yet. Add your first entry.")
        return

    st.markdown("### Strength Logs")
    st.dataframe(df, use_container_width=True)

    # progress chart per exercise
    st.markdown("### Progress Chart")

    exercise_options = df["exercise_name"].unique()
    selected_exercise = st.selectbox(
        "Select exercise to view progress",
        exercise_options
    )

    filtered_df = df[df["exercise_name"] == selected_exercise]

    fig = px.line(
        filtered_df,
        x="log_date",
        y="estimated_strength",
        markers=True,
        title=f"{selected_exercise} Strength Progress"
    )
    fig.update_layout(
        height=400,
        margin=dict(l=70, r=30, t=60, b=60),
        yaxis=dict(title="Estimated Strength"),
        xaxis=dict(title="Date")
    )
    st.plotly_chart(fig, use_container_width=True)

    # analytics
    st.markdown("### Analytics")
    start_strength = filtered_df["estimated_strength"].iloc[0]
    current_strength = filtered_df["estimated_strength"].iloc[-1]
    total_change = current_strength - start_strength

    col1, col2, col3 = st.columns(3)
    col1.metric("Start Strength", f"{start_strength:.1f}")
    col2.metric("Current Strength", f"{current_strength:.1f}")
    col3.metric("Total Change", f"{total_change:+.1f}")
