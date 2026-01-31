import pandas as pd
import ast
import math

def get_table_value(df, colname, error=None, format="%.3g"):

    if df.empty or pd.isna(df[colname].iloc[0]):
        return "-"

    val = df[colname].iloc[0]

    if error and not pd.isna(df[error].iloc[0]):
        err = df[error].iloc[0]

        try:
            return f"{format % val} ± {format % err}"
        except TypeError:
            pass

    return format % val

def get_table_list(df, colname, format="%.3g"):

    value_list = list(df[colname])

    print(value_list)

    return [(format % val) for val in value_list]


def get_converted_fluence(df, fluence, conversion):

    try:
        total_fluence = ast.literal_eval(df[fluence].iloc[0])[0]
        conv = df[conversion].iloc[0]
    except IndexError: # afterglow doesn't exist
        return "-" 

    if df.empty or math.isnan(total_fluence) or math.isnan(conv):
        return "-"
    
    if (not total_fluence > 0) or (not conv > 0):
        return "-"
    
    return '%.3g' % (total_fluence * conv)

def print_grb_name(name):

    if name.startswith("GRB"):
        name = name[3:]

    return "GRB " + name