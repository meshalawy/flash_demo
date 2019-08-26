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
mode = 'learn'

def get_visualization():
    global mode
    if mode=='learn':
        data = scenario_data['learning_data']
    else: 
        data = scenario_data['testing_data']
    fig = {
        "data": [{
                "type": "scattermapbox",
                "lat": [item['lat'] for item in data],
                "lon": [item['lon'] for item in data],
                "hoverinfo": "text",
                # "hovertext": [["Name: {} <br>Type: {} <br>Provider: {}".format(i,j,k)]
                                # for i,j,k in zip(map_data['Name'], map_data['Type'],map_data['Provider'])],
                "mode": "markers",
                # "name": list(map_data['Name']),
                # "color":"red",
                "marker": {
                    "size": 8,
                    "opacity": 0.8,
                    "color": [item['color'] for item in data],
                }
        }],
        "layout": dict(
                autosize=True,
                margin=dict(l=0,r=0,b=0,t=0),
                hovermode="closest",
                clickmode='event+select',
                mapbox=dict(
                    accesstoken=os.environ.get("mapbox_accesstoken"),
                    style="light",
                    center=scenario_data['map']['center'],
                    zoom=scenario_data['map']['zoom'],
                )
            )
    }
    config = {
        'modeBarButtonsToRemove': [] if mode == 'interactive-prediction' else ['select2d', 'lasso2d'],
        'displayModeBar': True if mode == 'interactive-prediction' else 'hover'
    }


    return [
        html.Div("Visualization", className="panel_title"),
        html.Div([dcc.Graph(id='graph', figure=fig, config=config)])
    ]


def get_flash_results():
    global mode
    if mode=='learn':
        df = pd.DataFrame(scenario_data['flash_learning_results'])
        title = 'Flash Learning Results'
    else:
        df = pd.DataFrame(scenario_data['flash_testing_results'])
        df = df.get([x for x in ['lat', 'lon', 'value', 'confidence'] if x in df.columns])
        title = 'Flash Predictiom Results'
    
    return [
        html.Div(title, className="panel_title"),
        dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                fixed_rows={ 'headers': True, 'data': 0 },
                style_cell={'width': '150px'}
            ) 
    ]


def get_competitor_results():
    global mode
    if mode=='learn':
        df = pd.DataFrame(scenario_data['competitor_learning_results'])
        title = 'Competitor Learning Results'
    else:
        df = pd.DataFrame(scenario_data['competitor_testing_results'])
        df = df.get([x for x in ['lat', 'lon', 'value', 'confidence'] if x in df.columns])
        title = 'Competitor Predictiom Results'
    
    return [
        html.Div(title, className="panel_title"),
        dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                fixed_rows={ 'headers': True, 'data': 0 },
                style_cell={'width': '150px'}
            )
    ]


def get_statistics():
    global mode
    if mode=='learn':
        df = pd.DataFrame(scenario_data['learning_statistics'])
    else:
        df = pd.DataFrame(scenario_data['predict_all_statistics'])
    
    df = df[["criteria","flash","competitor"]]
    return [
        # html.H5("Competitor Learning Results"),
        html.Div("Statistics", className="panel_title"),
        dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                fixed_rows={ 'headers': True, 'data': 0 },
                style_cell={'width': '150px'}
            ), 
        html.Div(id="selected_data"),
        
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
            children=[html.Img(src=app.get_asset_url("logo.png")), html.H3('FLASH')],
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
                            html.Div(get_visualization(), id="visualization",  className = "nine columns"),
                            html.Div(get_statistics(), id="statistics",  className = "three columns"),
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


@app.callback(
    [
        Output('visualization', 'children'),
        Output('flash_results', 'children'),
        Output('competitor_results', 'children'),
        Output('statistics', 'children'),
    ],[
        Input('learn-btn', 'n_clicks'),
        Input('predict-all-btn', 'n_clicks'),
        Input('interactive-prediction-btn', 'n_clicks')
    ],[
        State('training_data_upload', 'filename'),
    ]
)
def on_click_learn(n_clicks1, n_clicks2, n_clicks3, filename):
    global scenario_name, scenario_data, mode
    ctx = dash.callback_context


    if (not ctx.triggered) or not ctx.triggered[0]['value']  :
        raise PreventUpdate
    # if n_clicks1 is None:
    #     raise PreventUpdate

    triggered_by = ctx.triggered[0]['prop_id']
    if triggered_by == 'learn-btn.n_clicks':
        scenario_name = "default"
        if filename:
            scenario_name = filename.split('-')[0]
            
        scenario_data = json.load(open(DATA_PATH.joinpath(scenario_name, 'data.json')))
        time.sleep(3)
        mode='learn'
        return ([get_visualization(), get_flash_results(), get_competitor_results(), get_statistics()])
    
    elif triggered_by == 'predict-all-btn.n_clicks':
        mode='predict-all'
        return ([get_visualization(), get_flash_results(), get_competitor_results(), get_statistics()])

    elif triggered_by == 'interactive-prediction-btn.n_clicks':
        mode='interactive-prediction'
        return ([get_visualization(), get_flash_results(), get_competitor_results(), get_statistics()])


@app.callback(
    Output('selected_data', 'children'),
    [Input('graph', 'clickData')]
)
def graph_on_click(click_data):
    global scenario_data, mode
    if click_data and (mode=='predict-all' or mode=='interactive-prediction'):
        index = click_data['points'][0]['pointNumber']
        item = scenario_data['testing_data'][index]
        flash = scenario_data['flash_testing_results'][index]
        competitor = scenario_data['competitor_testing_results'][index]

        return [
            html.Div("Info", className="panel_title"),
            dash_table.DataTable(
                data=[
                    {'p': 'Ground Truth', 'v': item['value']},
                    {'p': 'Flash Prediction', 'v': flash.get('value')},
                    {'p': 'Flash Confidence', 'v': flash.get('confidence')},
                    {'p': 'Competitor Prediction', 'v': competitor.get('value')},
                    {'p': 'Competitor Confidence', 'v': competitor.get('confidence')},
                ],
                columns=[{'name': 'Property', 'id': 'p'}, {'name': 'Value', 'id': 'v'}],
                fixed_rows={ 'headers': False, 'data': 0 },
                style_cell={'width': '150px'}
            )]
    else: 
        return [""]
        
@app.callback(
    [
        Output('internals-monitoring', 'children'),
    ],[
        Input('graph', 'selectedData')
    ]
)
def graph_on_selections(selected_data):
    if selected_data and len(selected_data.keys()) > 1:
        print('finding the selected querter')
        return ['']
    else:
        return [""]


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
