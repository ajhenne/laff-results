import streamlit as st
import pandas as pd
import plotly.express as px
import os


st.set_page_config(page_title="LAFF Viewer", layout="wide")

pages = ["Burst Viewer", "Population Statistics"]
default_page = 0

@st.cache_data
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df


###############################################################################
### SIDEBAR 

st.sidebar.title("Navigation")

st.session_state.page = st.sidebar.radio("Go to", pages, index=default_page)

st.sidebar.divider()


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

if st.session_state.page == pages[0]:

    # search_query = st.text_input("Enter GRB Name:", "") # plain entry
    search_query = st.selectbox("Enter GRB Name:", name_options, index=None, placeholder='Enter GRB Name', label_visibility='collapsed')

    if search_query:

        search_query = search_query.strip().upper()
        search_query = search_query.replace(" ", "")
        search_query = search_query if search_query.startswith("GRB") else "GRB" + search_query
        search_query = search_query if search_query[-1].isalpha() else search_query + "A"

        afterglow = tab_afterglow[tab_afterglow['GRBname'].str.upper() == search_query]
        flares = tab_flares[tab_flares['GRBname'].str.upper() == search_query]
        pulses = tab_pulses[tab_pulses['GRBname'].str.upper() == search_query]

        if not all([afterglow.empty, flares.empty, pulses.empty]):

            st.header(f"{search_query}")

            xrt_path = os.path.join(dataset_path, "figures/xrt", f"{search_query}.png")
            bat_path = os.path.join(dataset_path, "figures/bat", f"{search_query}.png")

            col1, col2 = st.columns([2, 1])

            with col1:

                st.subheader('XRT Plot')
                if os.path.exists(xrt_path):
                    st.image(xrt_path, width='stretch')
                else:
                    st.error(f"No XRT fit for this burst.")

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

        st.container()
        st.header("LAFF Viewer")


        st.markdown("""
                    This tool allows you to explore the Swift-XRT and Swift-BAT for the complete set of bursts modelled by the Lightcurve and Flare Fitter (LAFF) code developed as part of my PhD thesis at the University of Leicester.

                    The plotted results are displayed where available for each instrument, as well as a summary table showing some general details of the burst alongside the LAFF fit parameters, statistics and some other calculated values. The T90 and redshift values are obtained from the [Swift-BAT GRB catalogue](https://swift.gsfc.nasa.gov/results/batgrbcat/), and the countrate-to-flux conversion factor for each burst is obtained from the Swift-XRT automatically fitted spectrum ([Evans et al. 2009](https://academic.oup.com/mnras/article/397/3/1177/1074442)). Hence, some of the calculated values such as flare fluence and isotropic energy are reliant on these values.

                    A full description of the LAFF fitting procedure can be found in Chapter 2 of my PhD thesis (*link available soon*).
                    """)

        st.divider()

        st.link_button("LAFF GitHub Repository", "https://github.com/ajhenne/laff/", icon=":material/code:")

        # 3. Call to Action



###############################################################################
### INDIVIDUAL BURST VIEWER

elif st.session_state.page == pages[1]:

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