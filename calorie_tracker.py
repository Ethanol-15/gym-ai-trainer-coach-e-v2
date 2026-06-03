import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
from supabase import create_client

# SUPABASE CONNECTION
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SAVE CALORIE GOALS

def save_calorie_goal(user_id, calorie_goal, protein_goal, carbs_goal, fats_goal):
     # Saves the user's calorie and macro goals
     # For now, this inserts a new goal row each time
     # Later, you can improve this to update the latest goal only
    try:
        # Check if an identical entry already exists
        existing = supabase.table("calorie_goals")\
            .select("calorie_goal, protein_goal, carbs_goal, fats_goal")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()

        if existing.data:
            latest = existing.data[0]
            if (
                latest["calorie_goal"] == calorie_goal and
                latest["protein_goal"] == protein_goal and
                latest["carbs_goal"] == carbs_goal and
                latest["fats_goal"] == fats_goal
            ):
                st.warning("⚠️ These goals are identical to your current settings. No changes made.")
                return

        supabase.table("calorie_goals").insert({
            "user_id": user_id,
            "calorie_goal": calorie_goal,
            "protein_goal": protein_goal,
            "carbs_goal": carbs_goal,
            "fats_goal": fats_goal
        }).execute()

    except Exception as e:
        st.error(f"Error saving calorie goal: {e}")

# LOAD LATEST CALORIE GOAL
def load_latest_calorie_goal(user_id):
    # Loads the most recent calorie goal for the logged-in user
    try:
        result = supabase.table("calorie_goals")\
            .select("calorie_goal, protein_goal, carbs_goal, fats_goal")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        if not result.data:
            return None
        return result.data[0]
    except Exception as e:
        st.error(f"Error loading calorie goal: {e}")
        return None

# SAVE DAILY CALORIE LOG
def save_calorie_log(user_id, log_date, calories, protein, carbs, fats):
    # Saves one daily calorie/macro log
    try:
        supabase.table("calorie_logs").insert({
            "user_id": user_id,
            "log_date": str(log_date),
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats
        }).execute()
    except Exception as e:
        st.error(f"Error saving calorie log: {e}")

# LOAD CALORIE LOGS
def load_calorie_logs(user_id):
    # Loads all calorie logs for the logged-in user
    # Converts result into pandas DataFrame for charts
    try:
        result = supabase.table("calorie_logs")\
            .select("log_date, calories, protein, carbs, fats")\
            .eq("user_id", user_id)\
            .order("log_date", desc=False)\
            .execute()
        if not result.data:
            return pd.DataFrame(columns=[
                "log_date", "calories", "protein", "carbs", "fats"
            ])
        df = pd.DataFrame(result.data)
        df["log_date"] = pd.to_datetime(df["log_date"])
        return df
    except Exception as e:
        st.error(f"Error loading calorie logs: {e}")
        return pd.DataFrame(columns=[
            "log_date", "calories", "protein", "carbs", "fats"
        ])

# MAIN CALORIE TRACKER PAGE
def render_calorie_tracker():
    # Back button
    if st.button("⬅ Back to Coach Chat"):
        st.session_state["page"] = "chat"
        st.rerun()
    user = st.session_state.get("user")
    st.markdown("## Calorie Tracker")
    # Block guest users
    if not user:
        st.warning("Please login to use the Calorie Tracker.")
        return
    user_id = user["id"]

    # GOAL SETTING FORM
    st.markdown("### Set Your Calorie & Macro Goals")
    with st.form("calorie_goal_form"):
        calorie_goal = st.number_input(
            "Daily Calorie Goal",
            min_value=1000,
            max_value=10000,
            step=50
        )
        protein_goal = st.number_input(
            "Protein Goal (g)",
            min_value=0.0,
            max_value=500.0,
            step=1.0
        )
        carbs_goal = st.number_input(
            "Carbs Goal (g)",
            min_value=0.0,
            max_value=1000.0,
            step=1.0
        )
        fats_goal = st.number_input(
            "Fats Goal (g)",
            min_value=0.0,
            max_value=300.0,
            step=1.0
        )
        goal_submitted = st.form_submit_button("Save Goals")

        if goal_submitted:
            save_calorie_goal(
                user_id,
                calorie_goal,
                protein_goal,
                carbs_goal,
                fats_goal
            )
            st.success("Calorie goals saved!")

    # Load latest goal after saving or page reload
    goal = load_latest_calorie_goal(user_id)
    if goal:
        st.info(
            f"Current Goal: {goal['calorie_goal']} kcal | "
            f"Protein: {goal['protein_goal']}g | "
            f"Carbs: {goal['carbs_goal']}g | "
            f"Fats: {goal['fats_goal']}g"
        )
    else:
        st.warning("Set your calorie goal first before tracking intake.")
   
    # DAILY LOGGING FORM
    st.markdown("### Log Today's Intake")
    with st.form("calorie_log_form"):
        log_date = st.date_input("Date", value=date.today())
        calories = st.number_input(
            "Calories Eaten",
            min_value=0,
            max_value=10000,
            step=50
        )
        protein = st.number_input(
            "Protein Eaten (g)",
            min_value=0.0,
            max_value=500.0,
            step=1.0
        )
        carbs = st.number_input(
            "Carbs Eaten (g)",
            min_value=0.0,
            max_value=1000.0,
            step=1.0
        )
        fats = st.number_input(
            "Fats Eaten (g)",
            min_value=0.0,
            max_value=300.0,
            step=1.0
        )

        log_submitted = st.form_submit_button("Save Intake")

        if log_submitted:
            save_calorie_log(
                user_id,
                log_date,
                calories,
                protein,
                carbs,
                fats
            )
            st.success("Calorie intake saved!")

    # LOAD AND DISPLAY LOGS
    df = load_calorie_logs(user_id)
    if df.empty:
        st.info("No calorie logs yet. Add your first intake.")
        return
    st.markdown("### Calorie Logs")
    st.dataframe(df, use_container_width=True)
   
    # TODAY'S REMAINING MACROS
    if goal:
        today_str = str(date.today())
        today_logs = df[df["log_date"].dt.date == date.today()]
        today_calories = today_logs["calories"].sum()
        today_protein = today_logs["protein"].sum()
        today_carbs = today_logs["carbs"].sum()
        today_fats = today_logs["fats"].sum()
        remaining_calories = goal["calorie_goal"] - today_calories
        remaining_protein = goal["protein_goal"] - today_protein
        remaining_carbs = goal["carbs_goal"] - today_carbs
        remaining_fats = goal["fats_goal"] - today_fats
        st.markdown("### Today's Remaining Intake")

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        col1.metric("Calories Left", f"{remaining_calories:.0f} kcal")
        col2.metric("Protein Left", f"{remaining_protein:.1f} g")
        col3.metric("Carbs Left", f"{remaining_carbs:.1f} g")
        col4.metric("Fats Left", f"{remaining_fats:.1f} g")

    # PROGRESS CHART
    st.markdown("### Calorie Progress Chart")
    fig = px.line(
        df,
        x="log_date",
        y="calories",
        markers=True,
        title="Calories Over Time"
    )
    fig.update_layout(
        height=400,
        margin=dict(l=70, r=30, t=60, b=60),
        yaxis=dict(title="Calories"),
        xaxis=dict(title="Date")
    )

    st.plotly_chart(fig, use_container_width=True)


    # ANALYTICS
    st.markdown("### Analytics")
    avg_calories = df["calories"].mean()
    avg_protein = df["protein"].mean()
    avg_carbs = df["carbs"].mean()
    avg_fats = df["fats"].mean()
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col1.metric("Avg Calories", f"{avg_calories:.0f} kcal")
    col2.metric("Avg Protein", f"{avg_protein:.1f} g")
    col3.metric("Avg Carbs", f"{avg_carbs:.1f} g")
    col4.metric("Avg Fats", f"{avg_fats:.1f} g")
