#app.py
# 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
from docx.shared import Inches
from shiny import App, render, ui, reactive
from shinywidgets import render_widget, output_widget
import numpy as np
import tempfile
from scipy.optimize import curve_fit
from plotnine import (ggplot, aes, geom_point, geom_line, geom_errorbar, labs,
                       theme, element_blank, element_line,element_text, 
                       element_rect, ylim,scale_y_log10)

from tmp import PKStudy
from plot_functions import plot_custom  # Import the custom plot function
from fit_functions import fit_data
from filter_functions import filter_study, filter_compound, filtered_data

#initial import for pulling out checkbox choices.
pk = PKStudy()
df = pk.study_all()
checkbox_mapping = {
    'COMPOUND_ID': 'Compound ID',
    "SRD_STUDY": 'Study ID',
    'STRAIN': 'Strain'
}

# Helper function to create a checkbox group for each column
def create_checkbox_groups(df, mapping):
    """Creates a list of checkbox groups for each column in the dataframe."""
    groups = []
    for column, label in mapping.items():
        groups.append(
            ui.input_selectize(
                id=column,
                label=label,
                choices=list(df[column].unique()),
                selected=df.loc[0,column],
                multiple=True
            )
        )
    return groups

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            create_checkbox_groups(df, checkbox_mapping),
            ui.input_slider("days", "Max # of Days", min=0, max=df['TIMEPOINT'].max(), value=14, step=1),
            ui.input_select("line_fit","Select Line Fit:",choices=['linear','spline','exponential','bi_exponential'],selected='linear'),
            ui.input_checkbox("logplot","Log Plot",False),
            ui.input_checkbox("error_bars", "Include Error Bars", True)
        ),
        ui.panel_main(
            ui.tags.h1("PK Visualization"),
            output_widget("plot"),
            ui.output_table("summary"),
            ui.download_button(id="download",label="Download CSV")
        )
    )
)

def server(input, output, session):
    """Server function for Shiny app."""
    input_df=pk.study_all()
    print('server is running')
    print(input_df.head())

    @reactive.Calc
    def reset_data():
        """Resets the dataframe to its original state."""
        df = pk.study_all()
        return df

    @reactive.Calc
    def filter():
        """Filters data based on selected compound or study."""
        df = input_df.copy()
        return filter_compound(df,input)
        #returm filter_study(df,input)

    @reactive.effect
    def update_compound_and_strain_options():
        """Updates compound and strain options based on selected study."""
        df = filter()
        new_study_ids = list(df['SRD_STUDY'].unique())
        new_strains = list(df['STRAIN'].unique())
        ui.update_selectize('SRD_STUDY', choices=new_study_ids, selected=new_study_ids)
        ui.update_selectize('STRAIN', choices=new_strains, selected=new_strains)

    @reactive.Calc
    def filtered_data():
        """Filters data based on timepoints. Could be consolidated possibly"""
        print('filtering selection')
        df=input_df.copy()
        df=df[df['TIMEPOINT']<=input.days()]
        for column in checkbox_mapping.keys():
            df = df[df[column].isin(input[column]())]
        return df
    
    @reactive.Calc
    def aggregate_data():
        """Aggregates filtered data."""
        df=filtered_data()
        agg_keys=list(checkbox_mapping.keys())
        agg_keys.append('TIMEPOINT')
        df = df.groupby(agg_keys).agg({'CONC': [
            ('average', 'mean'),   # Renaming the result columns directly in the aggregation
            ('count', 'count'),
            ('std', 'std')
        ]}).reset_index()

        df.columns = ['_'.join(col).rstrip('_') if isinstance(col, tuple) else col for col in df.columns.values]
        df=df.rename(columns={'CONC_average':'CONC'})
        df['CONC_count']=df['CONC_count'].astype(int)
        df['CONC_std'] = df['CONC_std'].fillna(0)  # Replace NaN std with 0
        return df
    
    @reactive.Calc
    def fit():
        """Fits data for plotting. See fit_functions.py"""
        df=aggregate_data()
        return fit_data(df)
    
    @render_widget
    def plot():
        """Renders the plot. See plot_functions.py"""
        print('plot data')
        df = fit()
        return plot_custom(df, input.error_bars(), input.logplot())
    
    summary_table_params=['SRD_STUDY','COMPOUND_ID','SPECIES','STRAIN','ANIMAL_ID','DOSE']
    summary_groupby=['SRD_STUDY','COMPOUND_ID','ANIMAL_ID']
    summary_agg = {
        'SPECIES': 'first',
        'STRAIN': 'first',
        'DOSE': 'first'
    }
    @output
    @render.table
    def summary():
        df=filtered_data()
        df=df[summary_table_params]
        df = df.groupby(summary_groupby).agg(summary_agg).reset_index()
        return df
    
    @render.download(filename="data.csv")
    def download():
        df = filtered_data()
        yield df.to_csv(index=False)
    
app=App(app_ui, server)
