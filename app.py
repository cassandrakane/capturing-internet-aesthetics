# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import matplotlib.image as img
import os
import pandas as pd
import random
import re
import requests
import sys
from scipy.cluster.vq import whiten
from scipy.cluster.vq import kmeans
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
            html.Div(id='container-button-basic')
        ], width=4)
    ])
], style={ 'margin' : '25px' })

def make_color(color):
    return html.Div(" ", className='colorBox', style={ 'margin' : '3px', 'padding' : '10px', 'background-color' : color })

def make_img(imgsrc):
    return 

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
        except:
            e = sys.exc_info()[0]
            # return "Error. The Instagram API limit has been reached; please wait a few hours or switch your internet network."
            return "Error: " + str(e)

        nodes = res["graphql"]["hashtag"]["edge_hashtag_to_top_posts"]["edges"]
        for n in nodes:
            img_file = img.imread(urlopen(n["node"]["thumbnail_src"]), 0)
            r = []
            g = []
            b = []
            for row in img_file:
                for temp_r, temp_g, temp_b in row:
                    r.append(temp_r)
                    g.append(temp_g)
                    b.append(temp_b)
            img_df = pd.DataFrame({'red' : r,
                                   'green' : g,
                                   'blue' : b})
            img_df['scaled_color_red'] = whiten(img_df['red'])
            img_df['scaled_color_blue'] = whiten(img_df['blue'])
            img_df['scaled_color_green'] = whiten(img_df['green'])
            cluster_centers, _ = kmeans(img_df[['scaled_color_red',
                                                'scaled_color_blue',
                                                'scaled_color_green']], 3)
            red_std, green_std, blue_std = img_df[['red',
                                                   'green',
                                                   'blue']].std()
            for cluster_center in cluster_centers:
                red_scaled, green_scaled, blue_scaled = cluster_center
                dominant_colors.append("rgb({}, {}, {})".format(int(red_scaled * red_std),
                                                                int(green_scaled * green_std),
                                                                int(blue_scaled * blue_std)))
    random.shuffle(dominant_colors)
    divs = []
    for color in dominant_colors:
        divs.append(make_color(color))
    return divs

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=True, host='0.0.0.0', port=port)
