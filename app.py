import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import plotly.express as px



import numpy as np
import pandas as pd
import pathlib

import base64
import io
import time
import os
import json

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)




server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Read data
# df = pd.read_csv(DATA_PATH.joinpath("clinical_analytics.csv"))

# Data that holds the selected scenario information
scenario_name = "default"
scenario_data = json.load(open(DATA_PATH.joinpath(scenario_name, 'data.json')))

def get_visualization():
    fig = {
        "data": [{
                "type": "scattermapbox",
                "lat": [item['lat'] for item in scenario_data['items']],
                "lon": [item['long'] for item in scenario_data['items']],
                "hoverinfo": "text",
                # "hovertext": [["Name: {} <br>Type: {} <br>Provider: {}".format(i,j,k)]
                                # for i,j,k in zip(map_data['Name'], map_data['Type'],map_data['Provider'])],
                "mode": "markers",
                # "name": list(map_data['Name']),
                "marker": {
                    "size": 6,
                    "opacity": 0.7
                }
        }],
        "layout": dict(
                autosize=True,
                margin=dict(
                    l=0,
                    r=0,
                    b=0,
                    t=0
                ),
                hovermode="closest",
                mapbox=dict(
                    accesstoken=os.environ.get("mapbox_accesstoken"),
                    style="light",
                    center=scenario_data['center'],
                    zoom=scenario_data['zoom'],
                )
            )
    }


    return [
        html.Div("Visualization", className="panel_title"),
        html.Div([dcc.Graph(id='graph', figure=fig)])
    ]


def get_flash_results():
    df = pd.read_csv(DATA_PATH.joinpath("clinical_analytics.csv"))
    return [
        html.Div("Flash Learning Results", className="panel_title"),
        dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                fixed_rows={ 'headers': True, 'data': 0 },
                style_cell={'width': '150px'}
            )
        
    ]


def get_competitor_results():
    df = pd.read_csv(DATA_PATH.joinpath("clinical_analytics.csv"))
    return [
        # html.H5("Competitor Learning Results"),
        html.Div("Competitor Learning Results", className="panel_title"),
        dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                fixed_rows={ 'headers': True, 'data': 0 },
                style_cell={'width': '150px'}
            )
        
    ]


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Br(),
            html.P("Training Data:"),
            dcc.Upload(
                id='training_data_upload',
                children=[
                    html.Button('Upload File', className="upload_button")
                ]
            ),
            html.Br(),

            html.P("Testing Data:"),
            dcc.Upload(
                id='testing_data_upload',
                children=[
                    html.Button('Upload File', className="upload_button")
                ]
            ),
            html.Br(),

            html.P("Graphical Model:"),
            dcc.Upload(
                id='graphical_model_upload',
                children=[
                    html.Button('Upload File', className="upload_button")
                ]
            ),
            html.Br(),


            html.P("Observations:"),
            dcc.Upload(
                id='observations_upload',
                children=[
                    html.Button('Upload File', className="upload_button")
                ]
            ),
            html.Br(),

            html.P("Model Params:"),
            dcc.Upload(
                id='model_params_upload',
                children=[
                    html.Button('Upload File', className="upload_button")
                ]
            ),
            html.Br(),

            
            html.Br(),

            html.P("Run Options:"),

            html.Button(id="learn-btn", children="Learn", n_clicks=0, className='button-primary'),
            html.Br(),
            html.Button(id="predict-all-btn", children="Predict All", n_clicks=0, className='button-primary'),
            html.Br(),
            html.Button(id="interactive-prediction-btn", children="Interactive Prediction", n_clicks=0, className='button-primary')
        ],
    )



app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url("logo.png")), html.H3('FLASH IN ACTION')],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="three columns",
            children=[
                generate_control_card(),
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="nine columns",
            children=[
                dcc.Tabs(id="tabs", children=[
                    dcc.Tab(
                        label='Basic Operation', 
                        id='basic-operation',
                        children=[
                            html.Div(get_visualization(), id="visualization",  className = "twelve columns"),
                            html.Div(get_flash_results(), id="flash_results", className = "six columns"),
                            html.Div(get_competitor_results(), id="competitor_results", className = "six columns"),
                        ]
                    ),
                    dcc.Tab(
                        label='Internals Monitoring',
                        id='internals-monitoring',
                        children=[
                           
                        ]),
                ]),
            ]),
    ],
)




def read_contents_csv_to_df(contents):
    df = None
    if contents:
            _, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return df


# @app.callback(
#     [Output('dataset-preview', 'children')],
#     [Input('upload', 'contents')],
# )
def show_file_preview(contents):
    df = read_contents_csv_to_df(contents)
    if df is not None:
        return [
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                fixed_rows={ 'headers': True, 'data': 0 },
                style_cell={'width': '150px'}
            )
        ]
    else:
        return [html.P("Select a file to preview")]


@app.callback(
    [
        Output('visualization', 'children'),
    ],[
        Input('learn-btn', 'n_clicks')
    ],[
        State('training_data_upload', 'filename'),
    ]
)
def on_click(n_clicks, filename):
    global scenario_name, scenario_data
    

    if n_clicks is None:
        raise PreventUpdate

    scenario_name = "default"
    if filename:
        scenario_name = filename.split('.')[0]
        
    scenario_data = json.load(open(DATA_PATH.joinpath(scenario_name, 'data.json')))
    return ([get_visualization()])

        


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
