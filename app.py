# -*- coding: utf-8 -*-

from colorthief import ColorThief
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import os
import random
import re
import requests
from urllib.request import urlopen

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY])
app.title = 'Capturing Internet Aesthetics'

app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col([
            html.H1(children='Capturing Internet Aesthetics'),
            html.H3(children='Translating Instagram Hashtags into Color Palettes'),
            html.P("Built by Cassandra Kane", style={ 'margin-top' : '10px' }),
            html.H5("Enter a hashtag:", style={ 'margin-top' : '20px' }),
            html.Div(dcc.Input(id='input-on-submit', type='text')),
            dbc.Button('Submit', id='submit-val', color="primary", style={ 'margin-top' : '5px' }, n_clicks=0),
            html.P("Color palettes may take a few minutes to generate...", style={ 'margin-top' : '10px' })
        ], width=7),
        dbc.Col([
            html.Div(id='container-button-basic', style={'display' : 'flex', 'flex-wrap' : 'wrap'})
        ], width=4)
    ])
], style={ 'margin' : '25px' })

def make_color(color):
    return html.Div(" ", className='colorBox', style={ 'width' : '10px', 'margin' : '3px', 'padding' : '10px', 'background-color' : color })

@app.callback(
    Output('container-button-basic', 'children'),
    Input('submit-val', 'n_clicks'),
    State('input-on-submit', 'value'))
def update_output(n_clicks, value):
    dominant_colors = []
    if value != None:
        res = None
        try:
            res = requests.get("https://www.instagram.com/explore/tags/{}/?__a=1".format(re.sub(r'[^\w\s]', '', value)), headers = {'User-agent': 'ig_hashtag_to_top_posts_0.1'}).json()
        except Exception as e:
            return "Error. The Instagram API limit has been reached; please wait a few hours or switch your internet network."

        nodes = res["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]
        for n in nodes:
            color_thief = ColorThief(urlopen(n["node"]["thumbnail_src"]))
            palette = color_thief.get_palette(color_count=3)
            dominant_colors.extend(palette)
    random.shuffle(dominant_colors)
    divs = []
    for color in dominant_colors:
        divs.append(make_color("rgb({}, {}, {})".format(color[0], color[1], color[2])))
    return divs

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=False, host='0.0.0.0', port=port)
