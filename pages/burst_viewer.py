import streamlit as st
import pandas as pd
import os

from random import randrange

from app import name_options, tab_afterglow, tab_flares, tab_pulses, dataset_path
from functions import get_table_list, get_table_value, get_converted_fluence, print_grb_name

# search_query = st.text_input("Enter GRB Name:", "") # plain entry
search_query = st.selectbox("Enter GRB Name:", name_options, index=None, placeholder='Enter GRB Name', label_visibility='collapsed')
# search_query = st.selectbox("Enter GRB Name:", name_options, index=randrange(len(name_options)-1), placeholder='Enter GRB Name', label_visibility='collapsed')

# st.divider()

if search_query:

    search_query = search_query.strip().upper()
    search_query = search_query.replace(" ", "")
    search_query = search_query if search_query.startswith("GRB") else "GRB" + search_query
    search_query = search_query if search_query[-1].isalpha() else search_query + "A"

    afterglow = tab_afterglow[tab_afterglow['GRBname'].str.upper() == search_query]
    flares = tab_flares[tab_flares['GRBname'].str.upper() == search_query]
    pulses = tab_pulses[tab_pulses['GRBname'].str.upper() == search_query]

    if not all([afterglow.empty, flares.empty, pulses.empty]):

        st.header(f"{print_grb_name(search_query)}")

        ### SUMMARY TABLE

        summary_left, summary_right = st.columns([0.5, 0.5], border=True)

        summary_data_left = {
            "T90 (s)": get_table_value(afterglow, 'T90', error="T90_err"),
            "Redshift": get_table_value(afterglow, 'redshift', error="redshift_err", format="%.2g"),
            "Afterglow Fluence (erg cm$^{-2}$)": get_converted_fluence(afterglow, 'fluence', 'conversion'),
        }

        summary_data_right = {
                "Pulse Count": len(pulses),
                "Flare Count": "-" if afterglow.empty else len(flares),
                "Afterglow Breaks": get_table_value(afterglow, 'breaknum', format='%d'),
        }

        with summary_left:
            for label, value in summary_data_left.items():
                    col1, col2 = st.columns([0.5, 0.5]) # Adjust ratios as needed
                    with col1:
                        st.markdown(f"**{label}**")
                    with col2:
                        st.text(value)
        with summary_right:
            for label, value in summary_data_right.items():
                    col1, col2 = st.columns([0.5, 0.5]) # Adjust ratios as needed
                    with col1:
                        st.markdown(f"**{label}**")
                    with col2:
                        st.text(value)

        st.divider()

        ###################################################################
        ### BAT SECTION

        st.subheader("Swift-BAT lightcurve")

        bat_image_path = os.path.join(dataset_path, "figures/bat", f"{search_query}.png")

        bat_plot, bat_table = st.columns([0.6, 0.4], border=True)

        with bat_plot:
            if os.path.exists(bat_image_path):
                st.image(bat_image_path, width='stretch')
            else:
                st.error("No BAT fit for this burst.")

        with bat_table:

            bat_conversion = get_table_value(pulses, 'conversion_bat')
            total_pulse_fluence = sum([x for x in pulses['fluence']])

            summary_data = {
                "BAT count-to-flux conversion": bat_conversion,
                "Total fluence in pulses": ("%.3g" % total_pulse_fluence) if (bat_conversion != "-" and not pd.isna(bat_conversion)) else "-",
                "Chi-Square": "tba"
                }

            # Display as a table-like layout
            for label, value in summary_data.items():
                col1, col2 = st.columns([0.5, 0.5]) # Adjust ratios as needed
                with col1:
                    st.markdown(f"**{label}**")
                with col2:
                    st.text(value)
            # collapse
            # model[1] parameters: rise, decay, sharp, amplitude
            # """

        pulse_table = pd.DataFrame({
            "Pulse Number": get_table_list(pulses, 'pulse_num', format='%d'),
            "Start Time (s)": get_table_list(pulses, 't_start'),
            "Peak Time (s)": get_table_list(pulses, 't_peak'),
            "End Time (s)": get_table_list(pulses, 't_stop'),
            "Duration (s)": get_table_list(pulses, 'duration'),
            "Decay/Rise Ratio": get_table_list(pulses, 't_ratio'),
            "Peak Flux (units)": get_table_list(pulses, 'peak_flux'),
            "Isotropic Energy (units)": get_table_list(pulses, 'e_iso'),
            "Peak Luminosity (units)": get_table_list(pulses, 'L_p'),
            "L_iso (units)": get_table_list(pulses, 'L_iso'),
            })
        
        pulse_table_model = pd.DataFrame({
            "Pulse Number": get_table_list(pulses, 'pulse_num', format='%d'),
            "t_peak": get_table_list(pulses, 't_peak'),
            "rise": get_table_list(pulses, 'rise'),
            "decay": get_table_list(pulses, 'decay'),
            "sharpness": get_table_list(pulses, 'sharp'),
            "amplitude": get_table_list(pulses, 'amplitude')
        })
    
        st.space()
        st.dataframe(pulse_table, hide_index=True)
    
        with st.expander('Function Parameters'):

            st.text("The pulses are modelled using a FRED function")

            st.latex(r"""
                        
                        F(t) =
                        \begin{cases}
                        A\times\exp\left(-\left(\frac{|t-t_m|}{r}\right)^s\right) & t \leq t_m\\
                        A\times\exp\left(-\left(\frac{|t-t_m|}{d}\right)^s\right) & t > t_m
                        \end{cases}
                        """)
            st.dataframe(pulse_table_model, hide_index=True)
        

        # GRBname,pulse_num,t_start,t_stop,t_peak,rise,decay,sharp,amplitude,fluence_rise,fluence_decay,chisq,rchisq,deltaAIC,BIC,Trig_ID,T90,T90_err,redshift,redshift_err,conversion,conversion_bat,bat_conversion_rchisq,dimple,t_rise,t_decay,duration,t_ratio,fluence,peak_flux,underlying_index,d_l,e_iso,L_p,L_iso,t_peak_z,t_start_z,t_end_z


        st.divider()

        ###################################################################



        xrt_path = os.path.join(dataset_path, "figures/xrt", f"{search_query}.png")

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

