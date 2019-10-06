# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from visualize_usau_module import ranking_data, appearance_hist, DIVISIONS, REGIONS

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
fig_rankings = ranking_data(division='MENS')
fig_hist = appearance_hist(division='MENS')

app.layout = html.Div(children=[
    html.H1(children='USAU Club Visualization'),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div(children='''
                    Select Division
                '''),

                dcc.Dropdown(
                    id='division_dropdown',
                    options=[{'label': d, 'value': d} for d in DIVISIONS],
                    value=DIVISIONS[0]),
            ]),
            dbc.Col([
                html.Div(children='''
                    Select Region
                    '''),
                dcc.Dropdown(
                    id='region_dropdown',
                    options=[{'label': r, 'value': r} for r in REGIONS] + [{'label': 'All Regions', 'value': 'all'}],
                    value='all')
            ])
        ])
    ]),
    html.Div([dcc.Graph(id='rankings_graph', figure=fig_rankings)]),
    html.Div([dcc.Graph(id='appearance_graph', figure=fig_hist)])
])


@app.callback([
    Output('rankings_graph', 'figure'),
    Output('appearance_graph', 'figure')],
    [Input('division_dropdown', 'value'), Input('region_dropdown', 'value')])
def update_figure(division, region):
    new_ranking = ranking_data(division, region)
    new_hist = appearance_hist(division, region)
    return new_ranking, new_hist


if __name__ == '__main__':
    app.run_server(debug=True)
