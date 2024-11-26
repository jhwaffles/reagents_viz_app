def get_custom_layout():
    # Define the marker shapes and colors
    marker_shapes = ['square', 'circle', 'diamond', 'cross', 'triangle-up', 'pentagon', 'x','triangle-se','hexagon']
    marker_colors = ['blue', 'red', 'orange', 'green', 'gray', 'purple', 'cyan', 'pink']

    def apply_custom_styles(fig):
        # Apply marker shapes and colors to traces
        for i, trace in enumerate(fig.data):
            shape = marker_shapes[i % len(marker_shapes)]  # Cycle through shapes
            color = marker_colors[i % len(marker_colors)]  # Cycle through colors
            trace.update(marker=dict(symbol=shape, color=color), line=dict(color=color))
        return fig

    # Define the layout with tight margins
    layout = dict(
        plot_bgcolor='white',
        width=800,
        height=300,
        margin=dict(
            l=40,  # Left margin
            r=40,  # Right margin
            t=40,  # Top margin
            b=40   # Bottom margin
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='LightPink',
            gridwidth=1,
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor='LightPink',
            showline=True,
            linecolor='black',
            linewidth=1,
            ticks='outside',
            tickwidth=1,
            tickcolor='black'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='LightBlue',
            gridwidth=1,
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor='LightPink',
            showline=True,
            linecolor='black',
            linewidth=1,
            ticks='outside',
            tickwidth=1,
            tickcolor='black'
        ),
        legend=dict(
            x=1.02,
            y=1,
            xanchor="left",
            yanchor="top",
            traceorder='normal',
            bgcolor='white',
            bordercolor='black',
            borderwidth=1
        )
    )

    return layout, apply_custom_styles