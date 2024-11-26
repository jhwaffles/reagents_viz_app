#app.py
# 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from shiny import App, render, ui, reactive
from shinywidgets import render_widget, output_widget
import numpy as np
import psycopg2
from functools import lru_cache
from layout import get_custom_layout
import matplotlib.pyplot as plt

conn = psycopg2.connect(database = "protein",  user = 'pd_upstream', password = 'uXrdHqYX69GMbWXz5FtQ', host = "athenadev", port = '5432')
db = conn.cursor()

#get list of runs from production_run_view
sql_query = f"SELECT * FROM pd_upstream.production_run_view"
dfi = pd.read_sql_query(sql_query, conn)

checkbox_mapping = {
    'product': 'product',
    'scale_liter': 'scale_liter',
    'strain': 'strain',
    'run_name':'run_name'
}
# Ensure all columns used in filters are properly prepared
for column, label in checkbox_mapping.items():
    if column != "scale_liter":  # Skip numeric columns
        dfi[column] = dfi[column].astype(str)

# Helper function to create a checkbox group for each column
def create_checkbox_groups(df, mapping):
    """Creates a list of checkbox groups for each column in the dataframe."""
    groups = []
    for column, label in mapping.items():
        groups.append(
            ui.input_selectize(
                id=column,
                label=label,
                choices=list(dfi[column].unique()),
                selected=dfi.loc[0,column],
                multiple=True
            )
        )
    return groups

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_selectize(id="product", label="Product", choices=[], multiple=True),
            ui.input_selectize(id="scale_liter", label="Scale (Liter)", choices=[], multiple=True),
            ui.input_selectize(id="strain", label="Strain", choices=[], multiple=True),
            ui.input_selectize(id="run_name", label="Run Name", choices=[], multiple=True)
        ),
        ui.panel_main(
            ui.tags.h1("Reagents Trend Viewer"),
            ui.layout_columns(
                ui.column(
                    6,
                    ui.input_selectize(id="y_var", label="Y Variable", choices=[], multiple=False),
                    ui.input_selectize(id="y_var_2", label="Y Variable 2", choices=[], multiple=False),
                ),
                ui.column(
                    6,
                    ui.input_checkbox(id="sync_axes", label="Sync x-axes for both graphs", value=False),
                    ui.input_slider(
                        id="x_range",
                        label="Set x-axis range (h)",
                        min=-12,  # Adjust as needed
                        max=60,  # Adjust as needed
                        value=[-12, 0],  # Default range
                        step=0.5
                    ),
                )
            ),
            output_widget("plot1"),
            output_widget("plot2"),
            ui.output_table("summary"),
            ui.download_button(id="download", label="Download CSV")
        )
    )
)

# Define the app server logic
def server(input, output, session):
    # Reactive: Fetch metadata from production_run_view
    # Caching metadata
    @lru_cache(maxsize=1)
    def fetch_metadata():
        sql_query = f"SELECT * FROM pd_upstream.production_run_view"
        return pd.read_sql_query(sql_query, conn)
    
    @reactive.Calc
    def get_metadata():
        sql_query = f"SELECT * FROM pd_upstream.production_run_view"
        data = pd.read_sql_query(sql_query, conn)
        return data

    # Cascaded filtering logic
    @reactive.Calc
    def filtered_by_product():
        df = get_metadata()
        selected_products = input.product()
        if selected_products:
            df = df[df['product'].isin(selected_products)]
        return df

    @reactive.Calc
    def filtered_by_scale():
        df = filtered_by_product()
        selected_scales = input.scale_liter()
        if selected_scales:
            selected_scales = [float(scale) for scale in selected_scales]
            df = df[df['scale_liter'].isin(selected_scales)]
        return df

    @reactive.Calc
    def filtered_by_strain():
        df = filtered_by_scale()
        selected_strains = input.strain()
        if selected_strains:
            df = df[df['strain'].isin(selected_strains)]
        return df

    @reactive.Calc
    def filtered_metadata():
        df = filtered_by_strain()
        selected_runs = input.run_name()
        selected_variables=['run_name','description','reactor_id','product','strain','site_of_run','scale_liter']
        if selected_runs:
            df = df[df['run_name'].isin(selected_runs)][selected_variables]
        return df

    # Update product filter options
    @reactive.Effect
    def update_product_choices():
        df = get_metadata()
        products = df['product'].unique().tolist()
        ui.update_selectize("product", choices=products, selected=[])

    # Update scale filter options
    @reactive.Effect
    def update_scale_choices():
        df = filtered_by_product()
        scales = df['scale_liter'].unique()
        ui.update_selectize("scale_liter", choices=list(map(str, scales)), selected=[])

    # Update strain filter options
    @reactive.Effect
    def update_strain_choices():
        df = filtered_by_scale()
        strains = df['strain'].unique().tolist()
        ui.update_selectize("strain", choices=strains, selected=[])

    # Update run_name filter options
    @reactive.Effect
    def update_run_name_choices():
        df = filtered_by_strain()
        run_names = df['run_name'].unique().tolist()
        ui.update_selectize("run_name", choices=run_names, selected=[])
    
    # Reactive: Fetch trend data for selected runs
    @reactive.Calc
    def trend_data():
        selected_runs = input.run_name()
        y_var = input.y_var()  # Selected Y variable from the UI
        y_var_2 = input.y_var_2()  # Selected Y variable from the UI

        if selected_runs:
            # Dynamically construct query to select only required columns
            columns_to_select = f'"post_feed_time_h_calculated", run_name, "{y_var}","{y_var_2}"'
            sql_query = f"""
                SELECT {columns_to_select}
                FROM pd_upstream.ferm_trends_online_bioreactor_data_view
                WHERE run_name IN ({','.join(["%s"] * len(selected_runs))})
            """
            df = pd.read_sql_query(sql_query, conn, params=selected_runs)
            return df

        return pd.DataFrame()  # Return an empty DataFrame if no runs are selected

    # Reactive: Generate Plotly chart

    @output
    @render_widget
    def plot1():
        df = trend_data()
        y_var = input.y_var()  # User-selected Y variable
                    
        # Filter out NULL values in the selected Y variable
        df = df.dropna(subset=[y_var])

        # Aggregate duplicate values by averaging them
        df = df.groupby(["post_feed_time_h_calculated", "run_name"], as_index=False).mean()

        if not df.empty and y_var:
            fig = px.line(
                df,
                x="post_feed_time_h_calculated",
                y=y_var,
                color="run_name",
                markers=True,  # Add markers to the line plot
                title=f"{y_var} vs Post Feed Time",
                labels={
                    "post_feed_time_h_calculated": "Time from Feed Start (h)",
                    y_var: y_var,
                    "run_name": "Run"
                },
            )
            
            # Apply the custom layout and styles
            plt.tight_layout(pad=0.5)
            layout, apply_styles = get_custom_layout()
            fig.update_layout(**layout)
             # Apply x-axis range if sync is enabled
            if input.sync_axes():
                x_min, x_max = input.x_range()
                fig.update_layout(xaxis=dict(range=[x_min, x_max]))
            
            fig = apply_styles(fig)
        
            return fig

        # Return a placeholder message if no data is available
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for selected runs or variable.",
            xref="paper", yref="paper",
            showarrow=False, font=dict(size=14)
        )
        return fig
    
    @output
    @render_widget
    def plot2():
        df = trend_data()
        y_var = input.y_var_2()  # User-selected Y variable
        # Filter out NULL values in the selected Y variable
        df = df.dropna(subset=[y_var])

        # Aggregate duplicate values by averaging them
        df = df.groupby(["post_feed_time_h_calculated", "run_name"], as_index=False).mean()
        if not df.empty and y_var:
            fig = px.line(
                df,
                x="post_feed_time_h_calculated",
                y=y_var,
                color="run_name",
                markers=True,  # Add markers to the line plot
                title=f"{y_var} vs Post Feed Time",
                labels={
                    "post_feed_time_h_calculated": "Time from Feed Start (h)",
                    y_var: y_var,
                    "run_name": "Run"
                },
            )
            plt.tight_layout(pad=0.5)
            layout, apply_styles = get_custom_layout()
            fig.update_layout(**layout)
            if input.sync_axes():
                x_min, x_max = input.x_range()
                fig.update_layout(xaxis=dict(range=[x_min, x_max]))
            fig = apply_styles(fig)
            return fig
        # Return a placeholder message if no data is available
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for selected runs or variable.",
            xref="paper", yref="paper",
            showarrow=False, font=dict(size=14)
        )
        return fig
    
    @output
    @render.table
    def summary():
        return filtered_metadata()

    @render.download(filename="data.csv")
    def download():
        df = trend_data()
        yield df.to_csv(index=False)

    # UI for selecting y-variable
    @reactive.Effect
    def update_y_var_choices():
        y_vars = [
            'od595-growth_data',
            'bioht_glucose_g_l-growth_data',
            'bioht_acetate_mmol-growth_data',
            'bioht_lactate_mmol-growth_data',
            'bioht_ammonia_mmol-growth_data',
            'bioht_glutamate_mmol-growth_data',
            'bioht_phosphate_mmol-growth_data',
            'bioht_magnesium_mmol-growth_data',
            'bioht_formate_mg_l-growth_data',
            'bioht_total_protein_g_l-growth_data',
            'temp_value-online_bioreactor_data',
            'stirr_value-online_bioreactor_data',
            'ph_value-online_bioreactor_data',
            'po2_value-online_bioreactor_data',
            'gasfl_value-online_bioreactor_data',
            'airflow_value_slpm-online_bioreactor_data',
            'o2flow_value_slpm-online_bioreactor_data',
            'feed_flow_rate-online_bioreactor_data',
            'feed_added_ml-online_bioreactor_data',
            'bioreactor_volume-online_bioreactor_data'
        ]
        ui.update_selectize("y_var", choices=y_vars, selected='od595-growth_data')  # Default to 'od595-growth_data'
        ui.update_selectize("y_var_2", choices=y_vars, selected='bioht_acetate_mmol-growth_data')  # Default to 'od595-growth_data'

    # Display connection status
    @output
    @render.text
    def status():
        if not get_metadata().empty:
            return "Data loaded successfully."
        else:
            return "No data available or failed to load data."
        
# Create the app
app = App(app_ui, server)