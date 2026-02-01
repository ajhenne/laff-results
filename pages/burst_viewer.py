import streamlit as st
import pandas as pd
import os
import ast

from random import randrange

from app import name_options, tab_afterglow, tab_flares, tab_pulses, dataset_path
from functions import get_table_multiple_values, get_table_value, get_table_list, get_converted_fluence, print_grb_name

# search_query = st.text_input("Enter GRB Name:", "") # plain entry
# search_query = st.selectbox("Enter GRB Name:", name_options, index=None, placeholder='Enter GRB Name', label_visibility='collapsed')
search_query = st.selectbox("Enter GRB Name:", name_options, index=randrange(len(name_options)-1), placeholder='Enter GRB Name', label_visibility='collapsed')

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
                    col1, col2 = st.columns([0.5, 0.5])
                    with col1:
                        st.markdown(f"**{label}**")
                    with col2:
                        st.text(value)
        with summary_right:
            for label, value in summary_data_right.items():
                    col1, col2 = st.columns([0.5, 0.5])
                    with col1:
                        st.markdown(f"**{label}**")
                    with col2:
                        st.text(value)

        st.markdown(":grey[:small[See [About LAFF](/laff_description) for a description of the model parameters, and the fitting procedure.]]")

        st.divider()

        ###################################################################
        ### BAT SECTION

        st.subheader("Swift-BAT")

        bat_image_path = os.path.join(dataset_path, "figures/bat", f"{search_query}.png")

        bat_plot, bat_table = st.columns([0.6, 0.4], border=True, vertical_alignment='center')

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

            for label, value in summary_data.items():
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    st.markdown(f"**{label}**")
                with col2:
                    st.text(value)

        if len(pulses):

            pulse_table = pd.DataFrame({
                "Pulse": get_table_multiple_values(pulses, 'pulse_num', format='%d'),
                "Start Time (s)": get_table_multiple_values(pulses, 't_start'),
                "Peak Time (s)": get_table_multiple_values(pulses, 't_peak'),
                "End Time (s)": get_table_multiple_values(pulses, 't_stop'),
                "Duration (s)": get_table_multiple_values(pulses, 'duration'),
                "Decay/Rise Ratio": get_table_multiple_values(pulses, 't_ratio'),
                "Fluence (erg/cm^2)": get_table_multiple_values(pulses, 'fluence'),
                "Peak Flux (erg/cm^2/s^1)": get_table_multiple_values(pulses, 'peak_flux'),
                "Isotropic Energy (erg)": get_table_multiple_values(pulses, 'e_iso'),
                "L_peak (erg/s)": get_table_multiple_values(pulses, 'L_p'),
                "L_iso (erg/s)": get_table_multiple_values(pulses, 'L_iso'),
                })
            
            pulse_table_model = pd.DataFrame({
                "Pulse Number": get_table_multiple_values(pulses, 'pulse_num', format='%d'),
                "t_peak": get_table_multiple_values(pulses, 't_peak'),
                "rise": get_table_multiple_values(pulses, 'rise'),
                "decay": get_table_multiple_values(pulses, 'decay'),
                "sharpness": get_table_multiple_values(pulses, 'sharp'),
                "amplitude": get_table_multiple_values(pulses, 'amplitude')
            })
        
            st.space()

            st.dataframe(pulse_table, hide_index=True)
        
            with st.expander('Function Parameters'):
                st.dataframe(pulse_table_model, hide_index=True)
            
        else:
            st.info("No pulses found for this burst.")
        
        st.divider()


        ###################################################################
        ### XRT SECTION

        st.subheader("Swift-XRT")

        if afterglow.empty and flares.empty:
            st.info("No XRT fit for this burst.")
        else:

            xrt_image_path = os.path.join(dataset_path, "figures/xrt", f"{search_query}.png")

            xrt_plot, xrt_table = st.columns([0.6, 0.4], border=True, vertical_alignment='center')

            with xrt_plot:
                if os.path.exists(xrt_image_path):
                    st.image(xrt_image_path, width='stretch')
                else:
                    st.error("No XRT fit for this burst.")


            with xrt_table:

                st.space()
                slopes_col, breaks_col = st.columns([0.5, 0.5])

                with slopes_col:

                    st.markdown("**Slope Indices**")
                    
                    slp_val, slp_err = st.columns([0.4, 0.6])
                    fmt = "%.3g"

                    with slp_val:
                        slopes = get_table_list(afterglow, 'slopes')
                        for v in slopes:
                            st.markdown(f"{fmt % v}")
                    with slp_err:
                        slopes_err = get_table_list(afterglow, 'slopes_err')
                        for e in slopes_err:
                            st.markdown(f"($\pm$ {fmt % e})")

                with breaks_col:

                    breaks = get_table_list(afterglow, 'breaks')
                    breaks_err = get_table_list(afterglow, 'breaks_err')

                    st.markdown("**Break Times (s)**")
                    
                    if not len(breaks):
                        st.text('-')
                    
                    brk_val, brk_err = st.columns([0.4, 0.6])
                    fmt = "%.3g"

                    with brk_val:
                        for v in breaks:
                            st.markdown(f"{fmt % v}")

                    with brk_err:
                        for e in breaks_err:
                            st.markdown(f"($\pm$ {fmt % e})")

                st.divider()

                summary_data = {
                    "Afterglow fluence (erg/cm^2)": get_converted_fluence(afterglow, 'fluence', 'conversion'),
                    "Total flare fluence (erg/cm^2)": "%.3g" % sum([x for x in flares['fluence']]),
                    }

                for label, value in summary_data.items():
                    col1, col2 = st.columns([0.5, 0.5])
                    with col1:
                        st.markdown(f"**{label}**")
                    with col2:
                        st.text(value)

            if len(flares):

                # indices,params,errors

                flare_table = pd.DataFrame({
                    "Flares": get_table_multiple_values(flares, 'flarenum', format='%d'),
                    "Start Time (s)": get_table_multiple_values(flares, 't_start'),
                    "Peak Time (s)": get_table_multiple_values(flares, 't_peak'),
                    "End Time (s)": get_table_multiple_values(flares, 't_end'),
                    "Duration (s)": get_table_multiple_values(flares, 'duration'),
                    "Underlying Index": get_table_multiple_values(flares, 'underlying_index'),
                    "Fluence (erg/cm^2)": get_table_multiple_values(flares, 'fluence'),
                    "Peak Flux (erg/cm^2/s^1)": get_table_multiple_values(flares, 'peak_flux'),
                    "Isotropic Energy (erg)": get_table_multiple_values(flares, 'e_iso'),
                    "L_peak (erg/s)": get_table_multiple_values(flares, 'L_p'),
                    "L_iso (erg/s)": get_table_multiple_values(flares, 'L_iso'),
                    })

                flare_params = [ast.literal_eval(x) for x in flares['params']]

                flare_table_model = pd.DataFrame({
                    "Flare Number": get_table_multiple_values(flares, 'flarenum', format='%d'),                    
                    "t_peak": [x[0] for x in flare_params],
                    "rise": [x[1] for x in flare_params],
                    "decay": [x[2] for x in flare_params],
                    "sharpness": [x[3] for x in flare_params],
                    "amplitude": [x[4] for x in flare_params],
                })
            
                st.space()

                st.dataframe(flare_table, hide_index=True)
            
                with st.expander('Function Parameters'):
                    st.dataframe(flare_table_model, hide_index=True)
                
            else:
                st.info("No pulses found for this burst.")
            
            st.divider()


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

    # 3. Call to Action

