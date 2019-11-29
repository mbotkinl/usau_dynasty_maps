# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from visualize_usau_module import ranking_data, appearance_hist, spirit_correlation, \
    COMP_DIVISIONS, get_divisions, get_regions

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

init_comp_division = COMP_DIVISIONS[0]
init_division = get_divisions(init_comp_division)[0]['value']
# print('init comp div', init_comp_division)
# print('init div', init_division)
fig_rankings = ranking_data(comp_division=init_comp_division, division=init_division)
fig_hist = appearance_hist(comp_division=init_comp_division, division=init_division)
fig_spirit = spirit_correlation(comp_division=init_comp_division, division=init_division)

app.layout = html.Div(style={'backgroundColor': 'white'}, children=[
    html.H1(children='USAU Visualization'),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div(children='''
                        Select Competitive Division
                    '''),

                dcc.Dropdown(
                    id='comp_division_dropdown',
                    options=[{'label': d, 'value': d} for d in COMP_DIVISIONS],
                    value=init_comp_division),
            ]),
            dbc.Col([
                html.Div(children='''
                    Select Sub-Division
                '''),

                dcc.Dropdown(
                    id='division_dropdown',
                    options=get_divisions(init_comp_division),
                    value=init_division),
            ]),
            dbc.Col([
                html.Div(children='''
                    Region of Team
                    '''),
                dcc.Dropdown(
                    id='region_dropdown',
                    options=get_regions(init_comp_division, init_division),
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
    [Input('comp_division_dropdown', 'value'), Input('division_dropdown', 'value'), Input('region_dropdown', 'value')])
def update_figure(comp_division, division, region):
    new_ranking = ranking_data(comp_division, division, region)
    new_hist = appearance_hist(comp_division, division, region)
    new_spirit = spirit_correlation(comp_division, division, region)
    return new_ranking, new_hist, new_spirit


@app.callback([Output('division_dropdown', 'options'),
               Output('division_dropdown', 'value')],
              [Input('comp_division_dropdown', 'value')])
def update_division_dropdown(comp_division):
    div_options = get_divisions(comp_division)
    # print('div options are')
    # print(div_options)
    return div_options, div_options[0]['value']


@app.callback([Output('region_dropdown', 'options'),
               Output('region_dropdown', 'value')],
              [Input('comp_division_dropdown', 'value'), Input('division_dropdown', 'value')])
def update_region_dropdown(comp_division, division):
    region_options = get_regions(comp_division, division)
    # print('region options are')
    # print(region_options)
    return region_options, region_options[0]['value']




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
