#filter_functions.py

def filter_study(df,input):
    """Filters the dataframe based on selected study IDs.

    Args:
        df (pd.DataFrame): The input dataframe.
        input (shiny.Input): Shiny input object containing user inputs.

    Returns:
        pd.DataFrame: The filtered dataframe based on selected study IDs.
    """

    if input['SRD_STUDY']():
        df = df[df['SRD_STUDY'].isin(input['SRD_STUDY']())]
    return df

def filter_compound(df,input):
    """Filters the dataframe based on selected compound IDs.

    Args:
        df (pd.DataFrame): The input dataframe.
        input (shiny.Input): Shiny input object containing user inputs.

    Returns:
        pd.DataFrame: The filtered dataframe based on selected compound IDs.
    """

    if input['COMPOUND_ID']():
        df = df[df['COMPOUND_ID'].isin(input['COMPOUND_ID']())]
    return df

def filtered_data(df,input,checkbox_mapping):
    """Filters the dataframe based on user selections for multiple columns.

    Args:
        df (pd.DataFrame): The input dataframe.
        input (shiny.Input): Shiny input object containing user inputs.
        checkbox_mapping (dict): Dictionary mapping column names to user-friendly labels.

    Returns:
        pd.DataFrame: The filtered dataframe based on user selections.
    """
    print('filtering selection')
    df=df[df['TIMEPOINT']<=input.days()]
    for column in checkbox_mapping.keys():
        df = df[df[column].isin(input[column]())]
    return df