import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

from datetime import date, datetime, time

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="GATE CSE Study Tracker",
    page_icon="📚",
    layout="wide"
)

# =====================================
# FILES
# =====================================

DATA_FILE = "study_log.csv"
SETTINGS_FILE = "settings.json"

# =====================================
# DEFAULT SETTINGS
# =====================================

DEFAULT_SETTINGS = {

    "gate_date": "2027-02-01",

    "subjects": [

        "Programming in C",
        "Data Structures",
        "Algorithms",
        "Digital Logic",
        "Computer Organization & Architecture",
        "Operating Systems",
        "Database Management Systems",
        "Computer Networks",
        "Theory of Computation",
        "Compiler Design",
        "Engineering Mathematics",
        "Discrete Mathematics",
        "General Aptitude"

    ],

    "activities": [

        "Learning",
        "Question Practice",
        "PYQs",
        "Revision",
        "Mock Test",
        "Error Analysis"

    ]

}

# =====================================
# CREATE FILES
# =====================================

if not os.path.exists(SETTINGS_FILE):

    with open(SETTINGS_FILE, "w") as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)

if not os.path.exists(DATA_FILE):

    df = pd.DataFrame(columns=[

        "Date",
        "Start Time",
        "End Time",
        "Duration",
        "Subject",
        "Activity",
        "Questions Attempted",
        "Correct Answers",
        "Notes"

    ])

    df.to_csv(DATA_FILE, index=False)

# =====================================
# LOAD DATA
# =====================================

with open(SETTINGS_FILE) as f:
    settings = json.load(f)

subjects = settings["subjects"]
activities = settings["activities"]

df = pd.read_csv(DATA_FILE)

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("📚 Study Tracker")

st.sidebar.header("Manage Subjects")

new_subject = st.sidebar.text_input("Add New Subject")

if st.sidebar.button("Add Subject"):

    new_subject = new_subject.strip()

    if new_subject == "":
        st.sidebar.warning("Enter a subject name.")

    elif new_subject in subjects:
        st.sidebar.warning("Subject already exists.")

    else:

        subjects.append(new_subject)
        settings["subjects"] = sorted(subjects)

        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)

        st.sidebar.success("Subject Added.")
        st.rerun()

if len(subjects):

    remove_subject = st.sidebar.selectbox(
        "Delete Subject",
        [""] + subjects
    )

    if st.sidebar.button("Delete Subject"):

        if remove_subject != "":

            settings["subjects"].remove(remove_subject)

            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)

            st.sidebar.success("Subject Removed.")
            st.rerun()

st.sidebar.markdown("---")

st.sidebar.info(
"""
Data is stored locally.

study_log.csv

settings.json
"""
)

# =====================================
# TITLE
# =====================================

st.title("🎯 GATE CSE Study Tracker")

st.caption("Track every study session and let the dashboard analyze your preparation.")

# =====================================
# LOG SESSION
# =====================================

st.subheader("Log Study Session")

with st.form("study_form", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:

        session_date = st.date_input(
            "Date",
            value=date.today()
        )

        start_time = st.time_input(
            "Start Time",
            value=time(9,0)
        )

        subject = st.selectbox(
            "Subject",
            subjects
        )

        attempted = st.number_input(
            "Questions Attempted",
            min_value=0,
            value=0,
            step=1
        )

    with col2:

        end_time = st.time_input(
            "End Time",
            value=time(11,0)
        )

        activity = st.selectbox(
            "Activity",
            activities
        )

        correct = st.number_input(
            "Correct Answers",
            min_value=0,
            value=0,
            step=1
        )

    notes = st.text_area(
        "Notes (Optional)"
    )

    submit = st.form_submit_button("Save Session")

    if submit:

        start_dt = datetime.combine(session_date, start_time)
        end_dt = datetime.combine(session_date, end_time)

        if end_dt <= start_dt:
            st.error("End time must be after start time.")
            st.stop()

        duration = round(
            (end_dt-start_dt).total_seconds()/3600,
            2
        )

        new_row = pd.DataFrame([{

            "Date": session_date,

            "Start Time": start_time.strftime("%H:%M"),

            "End Time": end_time.strftime("%H:%M"),

            "Duration": duration,

            "Subject": subject,

            "Activity": activity,

            "Questions Attempted": attempted,

            "Correct Answers": correct,

            "Notes": notes

        }])

        df = pd.concat([df,new_row],ignore_index=True)

        df.to_csv(DATA_FILE,index=False)

        st.success("Study session saved.")

        st.rerun()
# =====================================
# DAILY STUDY TREND
# =====================================

st.markdown("---")
st.subheader("📈 Daily Study Trend")

trend = (
    df.groupby("Date", as_index=False)["Duration"]
    .sum()
    .sort_values("Date")
)

fig = px.line(
    trend,
    x="Date",
    y="Duration",
    markers=True,
    title="Daily Study Trend"
)

fig.update_xaxes(
    tickformat="%d %b"
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Hours"
)

st.plotly_chart(fig, use_container_width=True)
# =====================================
# WEEKLY STUDY HOURS
# =====================================

st.markdown("---")
st.subheader("📆 Weekly Study Hours")

weekly = df.copy()

weekly["Week"] = (
    weekly["Date"]
    .dt.to_period("W")
    .astype(str)
)

weekly_hours = (
    weekly.groupby("Week", as_index=False)["Duration"]
    .sum()
)

fig = px.bar(
    weekly_hours,
    x="Week",
    y="Duration",
    text_auto=".1f",
    title="Weekly Study Hours"
)

fig.update_layout(
    xaxis_title="Week",
    yaxis_title="Hours",
    xaxis=dict(type="category")
)

st.plotly_chart(fig, use_container_width=True)
# =====================================
# MONTHLY STUDY HOURS
# =====================================

st.markdown("---")
st.subheader("🗓 Monthly Study Hours")

monthly = df.copy()

monthly["Month"] = (
    monthly["Date"]
    .dt.to_period("M")
    .dt.strftime("%b %Y")
)

monthly_hours = (
    monthly.groupby("Month", as_index=False)["Duration"]
    .sum()
)

fig = px.bar(
    monthly_hours,
    x="Month",
    y="Duration",
    text_auto=".1f",
    title="Monthly Study Hours"
)

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Hours",
    xaxis=dict(type="category")
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    monthly_hours.rename(
        columns={
            "Duration": "Hours"
        }
    ),
    hide_index=True,
    use_container_width=True
)

# =====================================
# DASHBOARD
# =====================================

st.markdown("---")
st.header("📊 Dashboard")

if not df.empty:

    # -------------------------
    # Data Preparation
    # -------------------------

    df["Date"] = pd.to_datetime(df["Date"])

    today = pd.Timestamp.today().normalize()

    this_week = today - pd.Timedelta(days=today.weekday())

    this_month = today.replace(day=1)

    gate_date = pd.to_datetime(settings["gate_date"])

    days_left = (gate_date - today).days

    # -------------------------
    # Hours
    # -------------------------

    total_hours = df["Duration"].sum()

    today_hours = df.loc[
        df["Date"] == today,
        "Duration"
    ].sum()

    week_hours = df.loc[
        df["Date"] >= this_week,
        "Duration"
    ].sum()

    month_hours = df.loc[
        df["Date"] >= this_month,
        "Duration"
    ].sum()

    # -------------------------
    # Questions
    # -------------------------

    attempted = df["Questions Attempted"].sum()

    correct = df["Correct Answers"].sum()

    wrong = attempted - correct

    accuracy = (
        correct / attempted * 100
        if attempted > 0
        else 0
    )

    # -------------------------
    # Sessions
    # -------------------------

    total_sessions = len(df)

    average_session = df["Duration"].mean()

    # -------------------------
    # Streak
    # -------------------------

    unique_days = sorted(
        df["Date"].dt.normalize().unique(),
        reverse=True
    )

    streak = 0

    check_day = today

    unique_days = set(unique_days)

    while check_day in unique_days:

        streak += 1

        check_day -= pd.Timedelta(days=1)

    # -------------------------
    # KPI CARDS
    # -------------------------

    row1 = st.columns(4)

    row1[0].metric(
        "⏳ Days Until GATE",
        max(days_left, 0)
    )

    row1[1].metric(
        "📚 Total Hours",
        f"{total_hours:.1f}"
    )

    row1[2].metric(
        "📝 Sessions",
        total_sessions
    )

    row1[3].metric(
        "🔥 Current Streak",
        f"{streak} Days"
    )

    row2 = st.columns(4)

    row2[0].metric(
        "Today's Hours",
        f"{today_hours:.1f}"
    )

    row2[1].metric(
        "This Week",
        f"{week_hours:.1f}"
    )

    row2[2].metric(
        "This Month",
        f"{month_hours:.1f}"
    )

    row2[3].metric(
        "Average Session",
        f"{average_session:.2f} hrs"
    )

    row3 = st.columns(4)

    row3[0].metric(
        "Questions Attempted",
        int(attempted)
    )

    row3[1].metric(
        "Correct",
        int(correct)
    )

    row3[2].metric(
        "Wrong",
        int(wrong)
    )

    row3[3].metric(
        "Accuracy",
        f"{accuracy:.1f}%"
    )

else:

    st.info("Start logging study sessions to see your dashboard.")
# =====================================
# ANALYTICS
# =====================================

st.markdown("---")
st.header("📈 Study Analytics")

if not df.empty:

    tab1, tab2, tab3 = st.tabs([
        "Subjects",
        "Activities",
        "Study Trend"
    ])

    # =================================
    # SUBJECT ANALYSIS
    # =================================

    with tab1:

        subject_hours = (
            df.groupby("Subject")["Duration"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig = px.bar(
            subject_hours,
            x="Subject",
            y="Duration",
            title="Study Hours by Subject",
            text_auto=".1f"
        )

        fig.update_layout(
            xaxis_title="Subject",
            yaxis_title="Hours"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            subject_hours.rename(
                columns={
                    "Duration": "Hours"
                }
            ),
            hide_index=True,
            use_container_width=True
        )

    # =================================
    # ACTIVITY ANALYSIS
    # =================================

    with tab2:

        activity_hours = (
            df.groupby("Activity")["Duration"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            activity_hours,
            values="Duration",
            names="Activity",
            hole=0.45
        )

        st.plotly_chart(fig, use_container_width=True)

        activity_table = activity_hours.rename(
            columns={
                "Duration": "Hours"
            }
        )

        st.dataframe(
            activity_table,
            hide_index=True,
            use_container_width=True
        )

    # =================================
    # DAILY TREND
    # =================================

    with tab3:

        daily = (
            df.groupby("Date")["Duration"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            daily,
            x="Date",
            y="Duration",
            markers=True,
            title="Daily Study Hours"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Hours"
        )

        st.plotly_chart(fig, use_container_width=True)

        weekday = df.copy()

        weekday["Weekday"] = weekday["Date"].dt.day_name()

        order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        weekday_hours = (
            weekday.groupby("Weekday")["Duration"]
            .sum()
            .reindex(order)
            .fillna(0)
            .reset_index()
        )

        fig = px.bar(
            weekday_hours,
            x="Weekday",
            y="Duration",
            title="Study Hours by Weekday",
            text_auto=".1f"
        )

        st.plotly_chart(fig, use_container_width=True)

else:

    st.info("Analytics will appear after you log some sessions.")
# =====================================
# REVISION DASHBOARD
# =====================================

st.markdown("---")
st.header("🔁 Revision Dashboard")

if not df.empty:

    latest = (
        df.groupby("Subject")["Date"]
        .max()
        .reset_index()
    )

    latest["Days Since"] = (
        pd.Timestamp.today().normalize() - latest["Date"]
    ).dt.days

    def revision_status(days):

        if days <= 2:
            return "🟢 Recently Studied"

        elif days <= 7:
            return "🟡 Revise Soon"

        else:
            return "🔴 Revision Due"

    latest["Status"] = latest["Days Since"].apply(
        revision_status
    )

    latest = latest.sort_values(
        "Days Since",
        ascending=False
    )

    st.dataframe(
        latest.rename(
            columns={
                "Date":"Last Studied"
            }
        ),
        hide_index=True,
        use_container_width=True
    )

    overdue = latest[latest["Days Since"] > 7]

    if len(overdue):

        st.warning(
            f"{len(overdue)} subject(s) have not been revised for more than a week."
        )

        st.write("Subjects needing attention:")

        st.write(", ".join(overdue["Subject"].tolist()))

    else:

        st.success("All subjects have been revised recently.")

else:

    st.info("Revision dashboard will appear after logging sessions.")
# =====================================
# HISTORY
# =====================================

st.markdown("---")
st.header("📜 Study History")

if not df.empty:

    col1, col2 = st.columns(2)

    with col1:

        subject_filter = st.selectbox(
            "Subject",
            ["All"] + sorted(df["Subject"].unique().tolist())
        )

    with col2:

        activity_filter = st.selectbox(
            "Activity",
            ["All"] + sorted(df["Activity"].unique().tolist())
        )

    history = df.copy()

    if subject_filter != "All":
        history = history[
            history["Subject"] == subject_filter
        ]

    if activity_filter != "All":
        history = history[
            history["Activity"] == activity_filter
        ]

    history = history.sort_values(
        "Date",
        ascending=False
    )

    st.dataframe(
        history,
        hide_index=True,
        use_container_width=True
    )

    csv = history.to_csv(index=False)

    st.download_button(
        "⬇ Download History",
        csv,
        "study_history.csv",
        "text/csv"
    )

else:

    st.info("No study history available.")
# =====================================
# SUBJECT PERFORMANCE
# =====================================

st.markdown("---")
st.header("🎯 Subject Performance")

if not df.empty:

    performance = (
        df.groupby("Subject")
        .agg(
            Hours=("Duration", "sum"),
            Sessions=("Subject", "count"),
            Attempted=("Questions Attempted", "sum"),
            Correct=("Correct Answers", "sum")
        )
        .reset_index()
    )

    performance["Accuracy"] = performance.apply(
        lambda x: round(
            x["Correct"] / x["Attempted"] * 100, 1
        ) if x["Attempted"] > 0 else 0,
        axis=1
    )

    performance = performance.sort_values(
        "Hours",
        ascending=False
    )

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No data available.")



# =====================================
# PERSONAL RECORDS
# =====================================

st.markdown("---")
st.header("🏆 Personal Records")

if not df.empty:

    longest = df.loc[df["Duration"].idxmax()]

    best_day = (
        df.groupby("Date")["Duration"]
        .sum()
        .idxmax()
    )

    best_day_hours = (
        df.groupby("Date")["Duration"]
        .sum()
        .max()
    )

    most_subject = (
        df.groupby("Subject")["Duration"]
        .sum()
        .idxmax()
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Longest Session",
        f"{longest['Duration']:.2f} hrs"
    )

    c2.metric(
        "Best Study Day",
        f"{best_day_hours:.2f} hrs"
    )

    c3.metric(
        "Most Studied Subject",
        most_subject
    )

    st.write("### Longest Session")

    st.write(longest)

else:

    st.info("No records yet.")
# =====================================
# CONSISTENCY
# =====================================

st.markdown("---")
st.header("📈 Study Consistency")

if not df.empty:

    last30 = pd.date_range(
        end=pd.Timestamp.today(),
        periods=30
    )

    studied = (
        df["Date"]
        .dt.normalize()
        .unique()
    )

    studied = set(studied)

    count = 0

    for d in last30:

        if d.normalize() in studied:
            count += 1

    consistency = count / 30 * 100

    st.progress(consistency / 100)

    st.metric(
        "Consistency",
        f"{consistency:.1f}%"
    )

else:

    st.info("Not enough data.")
st.markdown("---")

# =====================================
# QUICK PREVIEW
# =====================================

st.markdown("---")

st.subheader("Recent Sessions")

if len(df)==0:

    st.info("No study sessions logged yet.")

else:

    preview = df.sort_values("Date",ascending=False)

    st.dataframe(
        preview.tail(10).iloc[::-1],
        use_container_width=True,
        hide_index=True
    )
st.caption(
"""
GATE CSE Study Tracker

Built using Streamlit + Pandas + Plotly
"""
)
