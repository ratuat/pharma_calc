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

# === Onco Forecast Helpers ===
def months_to_annual_survival(months):
    if months <= 0:
        return 0.0
    return 0.5 ** (12 / months)

def forecast_treatment_needs(incidence_rate, prevalence, pfs, os, years=5):
    needs = []
    current_patients = prevalence
    for year in range(1, years + 1):
        new_cases = incidence_rate
        surviving_patients = current_patients * os
        patients_in_need = (new_cases + surviving_patients) * (1 - pfs)
        needs.append(patients_in_need)
        current_patients = new_cases + surviving_patients
    return needs

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

def plot_treatment_forecast(needs):
    years = list(range(1, len(needs) + 1))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(years, needs, marker='o', linestyle='-', color='darkred')
    ax.set_title('Forecast: Patients Needing Treatment Over 5 Years')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Patients')
    ax.grid(True)
    return fig

# === Streamlit App ===
st.title("MS & Oncology Metrics Dashboard")

# Sidebar Inputs
st.sidebar.header("MS Metrics Input")
relapses = st.sidebar.number_input("Total relapses", min_value=0, value=2)
patients = st.sidebar.number_input("Number of patients", min_value=1, value=100)
years = st.sidebar.number_input("Duration (years)", min_value=0.1, value=1.0)

cost_new = st.sidebar.number_input("Cost of new treatment ($)", min_value=0.0, value=50000.0)
cost_standard = st.sidebar.number_input("Cost of standard treatment ($)", min_value=0.0, value=30000.0)

qaly_new = st.sidebar.number_input("QALY of new treatment", min_value=0.0, value=1.5)
qaly_standard = st.sidebar.number_input("QALY of standard treatment", min_value=0.0, value=1.0)

new_lesions = st.sidebar.number_input("Number of new lesions", min_value=0, value=0)
edss_progression = st.sidebar.selectbox("Has EDSS progression occurred?", ["No", "Yes"]) == "Yes"

st.sidebar.header("EDSS Progression Input")
edss_input = st.sidebar.text_input("Enter EDSS scores separated by commas", value="2.0,2.5,3.0,3.2,3.4")
edss_values = [float(val.strip()) for val in edss_input.split(',') if val.strip() != ""]
edss_scores = {i * 24: score for i, score in enumerate(edss_values)}

# Oncological Forecast Inputs
st.sidebar.header("Oncology Forecast Input")
incidence_rate = st.sidebar.number_input("Incidence rate (new cases/year)", min_value=0, value=1000)
prevalence = st.sidebar.number_input("Current prevalence (total patients)", min_value=0, value=5000)
pfs_months = st.sidebar.number_input("Progression-Free Survival (PFS) in months", min_value=0.0, value=6.0)
os_months = st.sidebar.number_input("Overall Survival (OS) in months", min_value=0.0, value=18.0)

# === Calculations ===
arr = calculate_arr(relapses, patients, years)
icer = calculate_icer(cost_new, cost_standard, qaly_new, qaly_standard)
neda_status = check_neda(relapses, new_lesions, edss_progression)

# PFS/OS Conversion
pfs_rate = months_to_annual_survival(pfs_months)
os_rate = months_to_annual_survival(os_months)

forecast = forecast_treatment_needs(incidence_rate, prevalence, pfs_rate, os_rate)

# === Outputs ===
st.subheader("MS Metrics")
st.markdown(f"**ARR:** {arr:.4f}")
st.markdown(f"**ICER:** ${icer:.2f} per QALY")
st.markdown(f"**NEDA status:** {'✅ Achieved' if neda_status else '❌ Not achieved'}")

# ARR Plot
st.subheader("ARR Comparison")
arr_data = {'Standard': calculate_arr(20, 100, 2), 'New': arr}
st.pyplot(plot_arr_comparison(arr_data))

# EDSS Progression Graph
if len(edss_scores) > 1:
    st.subheader("EDSS Progression Graph")
    st.pyplot(plot_edss_progression(edss_scores))
else:
    st.info("Please enter at least two EDSS values separated by commas.")

# Oncology Forecast Output
st.subheader("Oncology Forecast")
for i, val in enumerate(forecast, start=1):
    st.markdown(f"**Year {i}:** {int(val)} patients needing treatment")

# Forecast Graph
st.pyplot(plot_treatment_forecast(forecast))
