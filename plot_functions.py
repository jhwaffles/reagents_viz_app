# plot_functions.py

import plotly.express as px
import plotly.graph_objects as go


def plot_custom(df, show_error_bars, use_log_scale):
    """Generates a Plotly line plot with custom options.

    Args:
        df (pd.DataFrame): Dataframe containing the data to plot.
        show_error_bars (bool): Whether to show error bars.
        use_log_scale (bool): Whether to use a logarithmic scale for the y-axis.

    Returns:
        plotly.graph_objects.Figure: The generated Plotly figure.
    """

    df = df.dropna(subset=['concentration'])

    # Calculate adjusted ymin and ymax for error bars
    df['ymin'] = df['concentration'] - df['concentration_std']
    df['ymax'] = df['concentration'] + df['concentration_std']
    
    # Ensure ymin for error bars does not go below 0
    df['ymin'] = df['ymin'].clip(lower=0)

    # Define the major ticks at every 7 days
    major_ticks = list(range(0, int(df['time'].max()) + 1, 7))
    major_ticks_labels = [str(day) for day in major_ticks]

    # Define minor ticks for every 1 day
    minor_ticks = list(range(0, int(df['time'].max()) + 1, 1))

    # Calculate y-axis limits considering the error bars
    y_min = max(0, df['ymin'].min())  # Ensure y_min is not negative
    y_max = df['ymax'].max()

    # Create the initial plotly figure
    fig = px.line(
        df, 
        x='time', 
        y='concentration', 
        color='compound', 
        symbol='STRAIN', 
        line_dash='SRD_STUDY',
        title='Mean Concentrations Over Time',
        labels={
            'time': 'Time after Dose (days)',
            'concentration': 'Concentration (ng/mL)',
            'compound': 'COMPOUND_ID',
            'STRAIN': 'Strain',
            'concentration_counts': 'Count'
        },
        hover_data={'concentration_counts': True}
    )
    
    # Add error bars if requested
    if show_error_bars:
        fig.update_traces(
            error_y=dict(
                type='data',
                array=df['concentration_std'],
                visible=True
            )
        )
    
    # Apply log scale if requested
    if use_log_scale:
        print('Applying log scale to plot', flush=True)
        fig.update_yaxes(type='log')

    # Customize the theme
    fig.update_layout(
        legend=dict(
            title=dict(text=''),
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.02  # Position the legend to the right
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            linecolor='black',
            linewidth=0.5,
            mirror=False,  # Do not mirror the axis lines
            tickvals=major_ticks,  # Set major ticks at every 7 days
            ticktext=major_ticks_labels,  # Labels for major ticks only
            ticks='outside',  # Show ticks outside the axis
            ticklen=6,  # Length of tick marks
            minor=dict(
                ticklen=4,  # Length of minor tick marks
                showgrid=False  # Hide grid lines for minor ticks
            ),
            tick0=0,  # Position of the first tick
            dtick=1,  # Interval between ticks
            showline=True,  # Ensure the line is shown
            showgrid=False  # Hide the grid
        ),
        yaxis=dict(
            linecolor='black',
            linewidth=0.5,
            mirror=False,  # Do not mirror the axis lines
            gridcolor='lightgray',
            gridwidth=0.5,
            ticks='outside',  # Show ticks outside the axis
            ticklen=6,  # Length of tick marks
            showline=True,  # Ensure the line is shown
            showgrid=False  # Hide the grid
        ),
        margin=dict(l=40, r=150, t=40, b=40),
        width=800,  # Set width to achieve 4:3 aspect ratio
        height=400  # Set height to achieve 4:3 aspect ratio
    )
    
    return fig