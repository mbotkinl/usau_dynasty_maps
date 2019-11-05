# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from visualize_usau_module import ranking_data, appearance_hist, spirit_correlation, DIVISIONS, REGIONS

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
fig_rankings = ranking_data(division=DIVISIONS[0])
fig_hist = appearance_hist(division=DIVISIONS[0])
fig_spirit = spirit_correlation(division=DIVISIONS[0])

app.layout = html.Div(style={'backgroundColor': 'white'}, children=[
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
                    Region of Team
                    '''),
                dcc.Dropdown(
                    id='region_dropdown',
                    options=[{'label': r, 'value': r} for r in REGIONS] + [{'label': 'All Regions', 'value': 'all'}],
                    value='all')
            ])
        ])
    ]),
    html.Div([dcc.Graph(id='rankings_graph', figure=fig_rankings)]),
    html.Div([dcc.Graph(id='appearance_graph', figure=fig_hist)]),
    html.Div([dcc.Graph(id='spirit_graph', figure=fig_spirit)])
])


@app.callback([
    Output('rankings_graph', 'figure'),
    Output('appearance_graph', 'figure'),
    Output('spirit_graph', 'figure')],
    [Input('division_dropdown', 'value'), Input('region_dropdown', 'value')])
def update_figure(division, region):
    new_ranking = ranking_data(division, region)
    new_hist = appearance_hist(division, region)
    new_spirit = spirit_correlation(division, region)
    return new_ranking, new_hist, new_spirit

#
# @app.callback([
#     Output('rankings_graph', 'figure'),
#     Output('appearance_graph', 'figure'),
#     Output('spirit_graph', 'figure')],
#     [Input('division_dropdown', 'value'),
#      Input('region_dropdown', 'value'),
#      Input('rankings_graph', 'clickData')])
# def update_figure(division, region, click_data):
#     curve_number = None
#     if click_data:
#         print(click_data)
#         curve_number = click_data['points'][0]['curveNumber']
#         print(curve_number)
#     new_ranking = ranking_data(division, region, curve_number)
#     new_hist = appearance_hist(division, region)
#     new_spirit = spirit_correlation(division, region)
#     return new_ranking, new_hist, new_spirit


if __name__ == '__main__':
    app.run_server(debug=True)
