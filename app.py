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

tab_afterglow = load_data("results/afterglow.csv")

###############################################################################
### SIDEBAR 

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Burst Viewer", "Population Results"])

###############################################################################
### INDIVIDUAL BURST VIEWER

if page == "Burst Viewer":
    st.title("GRB Afterglow Fit")
    
    search_query = st.text_input("Enter GRB Name (e.g., GRB210112A):", "").strip()

    if search_query:
        burst_data = tab_afterglow[tab_afterglow['GRBname'].str.upper() == search_query.upper()]

        if not burst_data.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"Fit Plot: {search_query}")
                # Path to your image
                img_path = f"figures/bat/{search_query}.png" # or .svg
                
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                else:
                    st.error(f"Image not found at {img_path}")
            
            with col2:
                st.subheader("Fit Parameters")
                st.table(burst_data.iloc[0])
                
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

    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Full Data Table"):
        st.dataframe(tab_afterglow)