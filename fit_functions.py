#fit_functions.property
 
import pandas as pd
import numpy as np


def fit_data(df):
    """Generates a fitted dataframe that distinguishes calculated and actual data.

    Args:
        df (pd.DataFrame): Dataframe containing the data to fit.

    Returns:
        pd.DataFrame: Dataframe which contains the fitted calculated data and actual data denoted in a new column called 'type'.
    """

    results = pd.DataFrame(columns=[
        'time', 'concentration', 'type', 'compound',
        'concentration_counts','study'
    ])
    equations = {}

    print('standard fit')
    for name, group_data in df.groupby(['COMPOUND_ID','STRAIN','SRD_STUDY']):  #group by what you want to plot by
        print(group_data)
        compound_id=name[0]
        strain=name[1]
        study=name[2]
        time = group_data['TIMEPOINT'].values
        concentration = group_data['CONC'].values
        concentration_std = group_data['CONC_std'].values
        concentration_counts = group_data['CONC_count'].values.astype(int)

        actual_data = pd.DataFrame({
            'time': time,
            'concentration': concentration, 
            'concentration_std': concentration_std,
            'concentration_counts': concentration_counts,
            'type': 'Actual', 
            'compound': compound_id,
            'STRAIN': strain,
            'SRD_STUDY':study
        })
        results = pd.concat([results, actual_data])

    return results


def bi_exp(x, A, alpha, B, beta):
    return A * np.exp(-alpha * x) + B * np.exp(-beta * x)