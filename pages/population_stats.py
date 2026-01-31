import streamlit as st
import plotly.express as px

from app import tab_afterglow, tab_flares, tab_pulses


st.title("Population Statistics")
st.write(f"Showing results for all {len(tab_afterglow)} bursts.")

# Select columns to plot
numeric_cols = tab_afterglow.select_dtypes(include=['float64', 'int64']).columns.tolist()

col1, col2, col3 = st.columns(3)
with col1:
    x_axis = st.selectbox("X-Axis Parameter", numeric_cols, index=0)
    x_log = st.segmented_control("Axis scale", ("Linear-scale", "Log-scale"), selection_mode='single', default='Log-scale', key='xlogtoggle', label_visibility='collapsed')
with col2:
    y_axis = st.selectbox("Y-Axis Parameter", numeric_cols, index=min(1, len(numeric_cols)-1))
    y_log = st.segmented_control("Axis scale", ("Linear-scale", "Log-scale"), selection_mode='single', default='Log-scale', key='ylogtoggle', label_visibility='collapsed')
with col3:
    color_by = st.selectbox("Color By (Optional)", ["None"] + numeric_cols)

fig = px.scatter(
    tab_afterglow, 
    x=x_axis, 
    y=y_axis, 
    color=None if color_by == "None" else color_by,
    hover_name="GRBname",  
    log_x=x_log == 'Log-scale',         
    log_y=y_log == 'Log-scale',
    template="plotly_dark",
)

st.plotly_chart(fig, width='stretch')


with st.expander("View Full Data Table"):
    st.dataframe(tab_afterglow)
