import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="GRB Fit Viewer", layout="wide")

@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df



###############################################################################
### SIDEBAR 

st.sidebar.title("Navigation")

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

st.sidebar.divider()

page = st.sidebar.radio("Go to", ["Burst Viewer", "Population Results"])



###############################################################################
### INDIVIDUAL BURST VIEWER

if page == "Burst Viewer":

    search_query = st.text_input("Enter GRB Name (e.g., GRB210112A):", "").strip().upper()

    if search_query:

        search_query = search_query.replace(" ", "")
        search_query = search_query if search_query.startswith("GRB") else "GRB" + search_query

        afterglow = tab_afterglow[tab_afterglow['GRBname'].str.upper() == search_query]
        flares = tab_flares[tab_flares['GRBname'].str.upper() == search_query]
        pulses = tab_pulses[tab_pulses['GRBname'].str.upper() == search_query]

        if not all([afterglow.empty, flares.empty, pulses.empty]):

            st.title(f"{search_query}")
            
            xrt_path = os.path.join(dataset_path, "figures/xrt", f"{search_query}.png")
            bat_path = os.path.join(dataset_path, "figures/bat", f"{search_query}.png")

            col1, col2 = st.columns([2, 1])

            with col1:

                st.subheader('XRT Plot')
                if os.path.exists(xrt_path):
                    st.image(xrt_path, width='stretch')
                else:
                    st.error(f"XRT fit not available for this burst.")

                st.subheader('BAT Plot')
                if os.path.exists(bat_path):
                    st.image(bat_path, width='stretch')
                else:
                    st.error(f"BAT fit not available for this burst.")

            with col2:
                
                st.subheader("Table Fit Values")

                st.table(afterglow.iloc[0])
                st.table(flares.iloc[0])
                st.table(pulses.iloc[0])
                
        else:
            st.warning(f"No data found for '{search_query}'.")
    else:
        st.info("Enter a GRB name to display the results.")

###############################################################################
### INDIVIDUAL BURST VIEWER

elif page == "Population Results":
    st.title("Population Statistics")
    st.write(f"Showing results for all {len(tab_afterglow)} bursts.")

    # Select columns to plot
    numeric_cols = tab_afterglow.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        x_axis = st.selectbox("X-Axis Parameter", numeric_cols, index=0)
    with col2:
        y_axis = st.selectbox("Y-Axis Parameter", numeric_cols, index=min(1, len(numeric_cols)-1))
    with col3:
        color_by = st.selectbox("Color By (Optional)", ["None"] + numeric_cols)

    fig = px.scatter(
        tab_afterglow, 
        x=x_axis, 
        y=y_axis, 
        color=None if color_by == "None" else color_by,
        hover_name="GRBname",  
        log_x=True,         
        log_y=True,
        template="plotly_dark",
        title=f"{y_axis} vs {x_axis}"
    )

    st.plotly_chart(fig, width='stretch')
    
    with st.expander("View Full Data Table"):
        st.dataframe(tab_afterglow)