from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_ag_grid as dag
from datetime import datetime, timedelta

df = pd.read_csv('Result.csv')
# Plotly graphs
df1 = df[df['Name_Plate']=='au']
df['Texto'] = 'Ciudad: ' + df['City'] + ', Fecha: ' + df['Date'] + ', Number of Quakes: ' +  (df['Count_Quakes']).astype(str) + ', Magnitude of Quakes: ' + (df['Magnitude_Mean']).astype(str)
# Create a sample date range
start_date = datetime(2015, 1, 1)
end_date = datetime(2025, 12, 31)
date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
# Create marks for the slider
marks = {
    i: date.strftime('%Y-%m-%d')
    for i, date in enumerate(date_range)
    if i % 365 == 0 # Show a mark every 30 days
}

# Assuming df has columns: Longitude, Latitude
fig = px.scatter_geo(df,
    lon="Longitude",
    lat="Latitude",
    scope="south america",  # sets projection region
    projection="natural earth",
    hover_data={'Longitude':False,'Latitude':False,'Texto':True}
)
# Style the markers
fig.update_traces(
    marker=dict(size=df['Magnitude_Mean'], color=df["IsPrediction"], 
                opacity=0.7, line=dict(width=0.5, color="gray"))
)

# Map aesthetics
fig.update_geos(
    showcountries=True, countrycolor="gray",
    showland=True, landcolor="lightgray",
    showocean=True, oceancolor="lightblue",
    showcoastlines=True, coastlinecolor="darkgray",
    lataxis=dict(range=[-55, 15]),
    lonaxis=dict(range=[-90, -25]),
)

# Layout polish
fig.update_layout(
    title=dict(
        text="Terremotos en Chile",
        x=0.5, xanchor="center",
        font=dict(size=20)
    ),
    margin=dict(l=0, r=0, t=40, b=0),
    height=600,
    template="plotly_white"
)

#fig = go.Figure([go.Scatter(x=df1['Date'], y=df1['Magnitude_Mean'])])
available_indicators = df['Name_Plate'].unique()
available_indicators2 = df['IsPrediction'].unique()

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
        html.Div(
        children="Earthquakes in Chile",
        style={
            "fontFamily": "Arial, sans-serif",  # change font
            "fontSize": "32px",                 # make it larger
            "fontWeight": "bold",               # bold text
            "color": "white",                   # text color
            "backgroundColor": "royalblue",       # background
            "textAlign": "center",              # center text
            "padding": "15px",                  # add spacing
            "borderRadius": "10px"              # rounded corners
        }
    ),
    html.Hr(),
    html.Div([
            html.Div([
                dcc.Dropdown(
                    id='column-options',
                    options=[{'label': i, 'value': i} for i in available_indicators],
                    value='au',  # Default to "Select All"
                    multi=True
                ),
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=start_date,
                    max_date_allowed=end_date,
                    initial_visible_month=datetime(2024, 1, 1),
                    start_date=start_date,
                    end_date=end_date,
                    display_format='YYYY-MM-DD'                 
                )          
            ],
            style={'width': '30%', 'display': 'inline-block',  'verticalAlign': 'top'}),
        html.Div([
            dcc.Dropdown(
                id='column-options2',
                options=[{'label': i, 'value': i} for i in available_indicators2],
                value='royalblue',  # Default to "Select All"
                multi=True
            )
            ], style={'width': '30%', 'float': 'right', 'display': 'inline-block',  'verticalAlign': 'top'})
            ], style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)'        }),
    html.Div([
        html.Div([
            dcc.Graph(figure=fig, id='graph1')
        ], style={'flex': '1', 'marginRight': '10px'}),
        html.Div([
        dag.AgGrid(
            id="grid",
            rowData=df.to_dict("records"),
            columnDefs=[{"field": i} for i in df.columns],
            style={"height": "600px", "overflowY": "auto"}  # scrollable table
        )], style={'flex': '1'})
    ], style={
        'display': 'flex',
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(251, 250, 250)'
    })
])

# Add controls to build the interaction
@callback(
    Output(component_id='graph1', component_property='figure'),
    Input(component_id='column-options', component_property='value'),
    Input(component_id='column-options2', component_property='value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
    
def update_graph(col_chosen, data_chosen, starting_date, ending_date):
    df3 = df[df['Date'].between(starting_date, ending_date)]
    if isinstance(col_chosen, list):
        df2 = df3[df3['Name_Plate'].isin(col_chosen)]
    else:
        df2 = df3[df3['Name_Plate']==col_chosen]
    if isinstance(data_chosen, list):
        df1 = df2[df2['IsPrediction'].isin(data_chosen)]
    else:
        df1 = df2[df2['IsPrediction']==data_chosen]

    # Assuming df has columns: Longitude, Latitude
    fig = px.scatter_geo(df1,
        lon="Longitude",
        lat="Latitude",
        scope="south america",  # sets projection region
        projection="natural earth",
        hover_data={'Texto':True}
    )
    # Style the markers
    fig.update_traces(
        marker=dict(size=df1['Magnitude_Mean'], color=df1["IsPrediction"], 
                    opacity=0.7, line=dict(width=0.5, color="gray"))
    )
    # Map aesthetics
    fig.update_geos(
        showcountries=True, countrycolor="gray",
        showland=True, landcolor="lightgray",
        showocean=True, oceancolor="lightblue",
        showcoastlines=True, coastlinecolor="darkgray",
        lataxis=dict(range=[-55, 15]),
        lonaxis=dict(range=[-90, -25]),
    )

    # Layout polish
    fig.update_layout(
        title=dict(
            text="Chilean Earthquakes",
            x=0.5, xanchor="center",
            font=dict(size=20)
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=600,
        template="plotly_white"
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
