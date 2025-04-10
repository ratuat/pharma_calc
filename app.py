import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# === MS Metrics Calculator ===
def calculate_arr(relapses: int, patients: int, years: float) -> float:
    return relapses / (patients * years)

def calculate_icer(cost_new: float, cost_standard: float, qaly_new: float, qaly_standard: float) -> float:
    delta_cost = cost_new - cost_standard
    delta_qaly = qaly_new - qaly_standard
    return delta_cost / delta_qaly if delta_qaly != 0 else float('inf')

def check_neda(relapses: int, new_lesions: int, edss_progression: bool) -> bool:
    return relapses == 0 and new_lesions == 0 and not edss_progression

# === Visualization Functions ===
def plot_arr_comparison(arr_dict):
    labels = list(arr_dict.keys())
    values = list(arr_dict.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color='skyblue')
    ax.set_title('Annualized Relapse Rate (ARR) Comparison')
    ax.set_ylabel('ARR')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    return fig

def plot_edss_progression(edss_scores):
    weeks = list(edss_scores.keys())
    scores = list(edss_scores.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(weeks, scores, marker='o', linestyle='-', color='green')
    ax.set_title('EDSS Progression Over Time')
    ax.set_xlabel('Weeks')
    ax.set_ylabel('EDSS')
    ax.grid(True)
    return fig

# === Streamlit App ===
st.title("MS Metrics Dashboard")

st.sidebar.header("Input Parameters")
relapses = st.sidebar.number_input("Total relapses", min_value=0, value=2)
patients = st.sidebar.number_input("Number of patients", min_value=1, value=100)
years = st.sidebar.number_input("Duration (years)", min_value=0.1, value=1.0)

cost_new = st.sidebar.number_input("Cost of new treatment ($)", min_value=0.0, value=50000.0)
cost_standard = st.sidebar.number_input("Cost of standard treatment ($)", min_value=0.0, value=30000.0)

qaly_new = st.sidebar.number_input("QALY of new treatment", min_value=0.0, value=1.5)
qaly_standard = st.sidebar.number_input("QALY of standard treatment", min_value=0.0, value=1.0)

new_lesions = st.sidebar.number_input("Number of new lesions", min_value=0, value=0)
edss_progression = st.sidebar.selectbox("Has EDSS progression occurred?", ["No", "Yes"]) == "Yes"

# Calculations
arr = calculate_arr(relapses, patients, years)
icer = calculate_icer(cost_new, cost_standard, qaly_new, qaly_standard)
neda_status = check_neda(relapses, new_lesions, edss_progression)

# Output Results
st.subheader("Calculated Metrics")
st.markdown(f"**ARR:** {arr:.4f}")
st.markdown(f"**ICER:** ${icer:.2f} per QALY")
st.markdown(f"**NEDA status:** {'Achieved' if neda_status else 'Not achieved'}")

# ARR Plot
st.subheader("ARR Comparison")
arr_data = {'Standard': calculate_arr(20, 100, 2), 'New': arr}
st.pyplot(plot_arr_comparison(arr_data))

# EDSS Progression Plot
st.subheader("EDSS Progression (Example)")
edss_scores = {0: 2.0, 24: 2.5, 48: 3.0, 72: 3.2, 96: 3.4}
st.pyplot(plot_edss_progression(edss_scores))
