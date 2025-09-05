import streamlit as st
import pandas as pd

# ===== Simple password protection =====
PASSWORD = "cowboy"

st.title("Football Benchmark App Login")
input_password = st.text_input("Enter password to continue:", type="password")

if input_password != PASSWORD:
    st.stop()

st.title("Football Benchmark App")
st.write("Select a position and a metric to view benchmark ranges or test a value.")

# ===== Load your Excel file with multiple sheets =====
excel_file = "benchmarks.xlsx"
all_sheets = pd.read_excel(excel_file, sheet_name=None)

# Clean up column names
for key in all_sheets:
    all_sheets[key].columns = all_sheets[key].columns.str.strip()

data_by_position = {
    "Centre Forward": all_sheets["Centre Forward"],
    "Centre Midfield": all_sheets["Centre Midfield"],
    "Winger": all_sheets["Winger"],
    "Full Back": all_sheets["Full Back"],
    "Centre Back": all_sheets["Centre Back"],
    "Goalkeeper": all_sheets["Goalkeeper"]
}

# ===== Handle session state for position and metric =====
if "position" not in st.session_state:
    st.session_state.position = "Centre Forward"

if "metric" not in st.session_state:
    st.session_state.metric = None

# Select position
selected_position = st.selectbox("Select Position", list(data_by_position.keys()), index=list(data_by_position.keys()).index(st.session_state.position))
st.session_state.position = selected_position

df = data_by_position[selected_position]
metrics = df["Metric"].tolist()

# Update metric dropdown only if the current metric is not in the new metric list
if st.session_state.metric not in metrics:
    st.session_state.metric = metrics[0]

selected_metric = st.selectbox("Select Metric", metrics, index=metrics.index(st.session_state.metric))
st.session_state.metric = selected_metric

# ===== Show benchmark ranges =====
row = df[df["Metric"] == selected_metric].iloc[0]

st.subheader(f"Ranges for {selected_metric}")
st.markdown(f"<span style='color:red'>Poor:</span> {row['Poor (<10%)']}", unsafe_allow_html=True)
st.markdown(f"<span style='color:orange'>Below Average:</span> {row['Below Average']}", unsafe_allow_html=True)
st.markdown(f"<span style='color:grey'>Average:</span> {row['Average']}", unsafe_allow_html=True)
st.markdown(f"<span style='color:blue'>Good:</span> {row['Good']}", unsafe_allow_html=True)
st.markdown(f"<span style='color:green'>Excellent:</span> {row['Excellent (>90%)']}", unsafe_allow_html=True)
st.write("**Sustainable Good Range (30-90%)**:", row["Sustainable Good Range (30-90%)"])

# ===== Persistent value input =====
if "metric_value" not in st.session_state:
    st.session_state.metric_value = 0.0

st.session_state.metric_value = st.number_input(
    "Enter your value for this metric", 
    step=0.01,
    value=st.session_state.metric_value,
    key="metric_value"
)

def get_category(val, r):
    def parse_range(text):
        if "-" in text:
            parts = text.split(' ')[0].split('-')
            return float(parts[0]), float(parts[1])
        return None, None

    try:
        poor_upper = float(r['Poor (<10%)'].split(' ')[1])
    except:
        poor_upper = None

    below_low, below_high = parse_range(r['Below Average'])
    avg_low, avg_high = parse_range(r['Average'])
    good_low, good_high = parse_range(r['Good'])

    try:
        exc_threshold = float(r['Excellent (>90%)'].split(' ')[1])
    except:
        exc_threshold = None

    if poor_upper is not None and val < poor_upper:
        return "Poor", "red"
    if below_low is not None and below_low <= val <= below_high:
        return "Below Average", "orange"
    if avg_low is not None and avg_low <= val <= avg_high:
        return "Average", "grey"
    if good_low is not None and good_low <= val <= good_high:
        return "Good", "blue"
    if exc_threshold is not None and val > exc_threshold:
        return "Excellent", "green"
    return "Out of Range", "black"

if st.session_state.metric_value is not None and st.session_state.metric_value != 0:
    category, color = get_category(st.session_state.metric_value, row)
    st.markdown(f"**Your category:** <span style='color:{color}'>{category}</span>", unsafe_allow_html=True)
