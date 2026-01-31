import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="LAFF Viewer", layout="wide")

# pages = ["Burst Viewer", "Population Statistics"]
# default_page = 0

@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df


###############################################################################
### DATASET SELECTION 

datasets = [dt for dt in os.listdir('results')]

def beautify_dataset_name(folder_name):
    date, version = folder_name.split('_')
    yy = date[:2]
    mm = date[2:4]
    return f"{mm}/20{yy} (laff v{version})"
dataset_name_map = {beautify_dataset_name(d): d for d in datasets}

selected_dataset = st.sidebar.selectbox("Select dataset", options=dataset_name_map.keys())
dataset_path = os.path.join('results', dataset_name_map[selected_dataset])

tab_afterglow = load_data(dataset_path + "/afterglow.csv")
tab_flares = load_data(dataset_path + "/flares.csv")
tab_pulses = load_data(dataset_path + "/pulses.csv")

combined_names = tab_afterglow['GRBname'].unique().tolist() + tab_flares['GRBname'].unique().tolist() + tab_pulses['GRBname'].unique().tolist()
name_options = sorted(set(combined_names))
name_options = [x[0:3] + ' ' + x[3:] for x in name_options]

###############################################################################
### INDIVIDUAL BURST VIEWER



pg = st.navigation([
    st.Page('pages/burst_viewer.py', title="Burst Viewer"),
    st.Page('pages/population_stats.py', title='Population Statistics')],
    )
pg.run()    