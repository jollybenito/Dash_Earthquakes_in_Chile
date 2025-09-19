# Plotly's Figure Friday challenge. See more info here: https://community.plotly.com/t/figure-friday-2024-week-32/86401
import dash
import pandas as pd
import numpy as np
from dash import Dash, html, dcc, Input, Output, State, callback, Patch
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.graph_objects as go
import plotly.express as px

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

df = pd.read_csv('Result.csv')
df['City'] = df["City"].astype(str)
numeric_columns = [
   'Count_Quakes', 'Magnitude_Mean'
]


plate_dropdown = html.Div(
    [
        dbc.Label("Select a Tectonic plate", html_for="plate_dropdown"),
        dcc.Dropdown(
            id="plate-dropdown",
            options=sorted(df["Name_Plate"].unique()),
            value='au',
            clearable=False,
            maxHeight=600,
            optionHeight=50
        ),
    ],  className="mb-4",
)

year_radio = html.Div(
    [
        dbc.Label("Select Year", html_for="date-checklist"),
        dcc.Dropdown(
            id="year-dropdown",
            options=sorted(df["Year"].unique()),
            value=2025,
            clearable=False,
            maxHeight=600,
            optionHeight=50
        ),
    ],
    className="mb-4",
)

control_panel = dbc.Card(
    dbc.CardBody(
        [year_radio, plate_dropdown ],
        className="bg-light",
    ),
    className="mb-4"
)

heading = html.H1("Earthquakes history and predicition",className="bg-secondary text-white p-2 mb-4")

about_card = dcc.Markdown(
    """
    A side project in which I present earthquake data from Chile. And try to create an accurate predictor for future earthquakes"
    """)

data_card = dcc.Markdown(
    """
    Data was obtained from Kaggle user: nicolasgonzalezmunoz go ahead and check the source below!
     [Data source](https://www.kaggle.com/datasets/nicolasgonzalezmunoz/earthquakes-on-chile/)
    
    The boundaries for the tectonic plates were obtained from another Kaggle user: cwthompson please also go ahead and check it too!
     [Data source] (https://www.kaggle.com/datasets/cwthompson/tectonic-plate-boundaries/data/)

    The code for this dash can be reviewed, branched or used for reference from here:
     [Data source GitHub](https://github.com/)
    """
)

info = dbc.Accordion([
    dbc.AccordionItem(about_card, title="About this project", ),
    dbc.AccordionItem(data_card, title="Data Source")
],  start_collapsed=True)

def make_grid():
    grid = dag.AgGrid(
        id="grid",
        rowData=df.to_dict("records"),
        columnDefs=[
          {"field": "City", "cellRenderer": "markdown", "linkTarget": "_blank",  "initialWidth":250, "pinned": "left" },
          {"field": "Name_Plate", "cellRenderer": "markdown", "linkTarget": "_blank",  "initialWidth":250, "pinned": "left" },
          {"field": "Year" }, {"field": "Month" }] +
        [{"field": c} for c in numeric_columns],
        defaultColDef={"filter": True, "floatingFilter": True,  "wrapHeaderText": True, "autoHeaderHeight": True, "initialWidth": 125 },
        dashGridOptions={},
        filterModel={'Year': {'filterType': 'number', 'type': 'equals', 'filter': 2023}},
        rowClassRules = {"bg-secondary text-dark bg-opacity-25": "params.node.rowPinned === 'top' | params.node.rowPinned === 'bottom'"},
        style={"height": 600, "width": "100%"}
    )
    return grid

app.layout = dbc.Container(
    [
        dcc.Store(id="city-selected", data={}),
        heading,
        dbc.Row([
            dbc.Col([control_panel, info], md=3),
            dbc.Col(
                [
                    dcc.Markdown(id="title"),
                    dbc.Row([dbc.Col( html.Div(id="distance-card"))]),
                    html.Div(id="predictions-card", className="mt-4"),
                ],  md=9
            ),
        ]),
        dbc.Row(dbc.Col( make_grid()), className="my-4")
    ],
    fluid=True,
)

@callback(
    Output("grid", "dashGridOptions"),
    Output("city-selected", "data"),
    Input("plate-dropdown", "value"),
    Input("year-dropdown", "value"),
)
def pin_selected_report(city, yr):
    dff = df[(df["City"] == city) & (df['Year'] == yr)]
    dff = dff.fillna('')
    records = dff.to_dict("records")
    return {"pinnedTopRowData": records}, records

@callback(
    Output("grid", "dashGridOptions", allow_duplicate=True),
    Input("grid", "virtualRowData"),
    prevent_initial_call=True
)
def row_pinning_bottom(data):
    pinned_data = []
    if data:
        dff = pd.DataFrame(data) if data else df
        medians = dff[numeric_columns].to_dict()
        if medians:
            pinned_data = [{"City": "Median", **medians}]

    grid_option_patch = Patch()
    grid_option_patch["pinnedBottomRowData"] = pinned_data
    return grid_option_patch


@callback(
    Output("grid", "filterModel"),
    Input("year-dropdown", "value"),
    State("grid", "filterModel"),
)
def update_filter_model(year, model):
    if model:
        model["Year"] = {"filterType": "number", "type": "equals", "filter": year}
        return model
    return dash.no_update

@callback(
    Output("predictions-card", "children"),
    Input("city-selected", "data")
)
def predictions_chart(data):
    if data is None or data == {}:
        fig = {}
    else:
        #data = data[0]
        #fig = px.histogram(data, x="Month")
        #fig.update_layout(bargap=0.2)
        pass
    return dbc.Card([
        dbc.CardHeader(html.H2("Temporary text"), className="text-center"),
        #dcc.Graph(figure=fig, style={"height":250}, config={'displayModeBar': False})
    ])


@callback(
    Output("title", "children"),
    Input("city-selected", "data")
)
def make_title(data):
    data=data[0]
    title = f"""
    ## {data["Year"]} Earthquakes in {data["City"]}) 
    """
    return title


@callback(
    Output("distance-card", "children"),
    Input("city-selected", "data")
)
def make_distance_card(data):
    if not data:  # Check if the list is empty
        return dbc.Card([
            dbc.CardHeader(html.H2("No data to display"), className="text-center"),
        ])

    data = data[0]
    data = {k: (f"{v}%" if v  else '') for k, v in data.items()}
    hours_t = dbc.Row([
        html.Div("Proportion of Count_Quakes:", className="mb-1"),
        dbc.Col([
            html.Div("Count_Quakes", className=" border-bottom border-3"),
            html.Div("Mean Hours"),
            html.Div("Benefits In Kind"),

        ], style={"minWidth": 250}),
        dbc.Col([
            html.Div("Men", className=" border-bottom border-3"),
            html.Div( f"{data['Count_Quakes']}"),
            html.Div(f"{data['Count_Quakes']}"),

        ]),
        dbc.Col([
            html.Div("Women", className=" border-bottom border-3"),
            html.Div(f"{data['Count_Quakes']}"),
            html.Div(f"{data['Count_Quakes']}"),

        ])
    ], style={"minWidth": 400})

    mean = dbc.Alert(dcc.Markdown(
        f"""
        ** Mean Count_Quakes **  
        ### {data['Count_Quakes']}  
        This gives context
        """,
    ), color="dark")

    median = dbc.Alert(dcc.Markdown(
        f"""
        ** Count_Quakes **  
        ### {data['Count_Quakes']}  
        This gives context
        """,
    ), color="dark")

    card =  dbc.Card([
        dbc.CardHeader(html.H2("Header name 2"), className="text-center"),
        dbc.CardBody([
            dbc.Row([dbc.Col(mean), dbc.Col(median)], className="text-center"),
            hours_t
        ])
    ])
    return card


if __name__ == "__main__":
    app.run(debug=True)
    