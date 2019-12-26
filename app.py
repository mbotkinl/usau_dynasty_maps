# -*- coding: utf-8 -*-
import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd

from visualize_usau_module import ranking_data, spirit_correlation, \
    COMP_DIVISIONS, get_divisions, get_regions, table_data, BACKGROUND_COLOR_DARK, BACKGROUND_COLOR_LIGHT, \
    PLOT_BACKGROUND_COLOR

# style = {}
style = {'backgroundColor': BACKGROUND_COLOR_LIGHT}
# external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.4.1/flatly/bootstrap.min.css']
# external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

init_comp_division = COMP_DIVISIONS[0]
init_division = get_divisions(init_comp_division)[0]['value']

df = table_data(init_comp_division, init_division)
fig_rankings = ranking_data(comp_division=init_comp_division, division=init_division, highlight_teams=df.Team.tolist())
fig_spirit = spirit_correlation(comp_division=init_comp_division, division=init_division)

app.layout = html.Div(style=style, children=[
    html.H1(children='USAU Visualization', style={'backgroundColor': BACKGROUND_COLOR_DARK,
            'textAlign': 'center', 'font-weight': 'bold', 'font-size': '65px'}),
    html.Hr(),
    html.Hr(),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div(children='''
                        Select Competitive Division
                    '''),

                dcc.Dropdown(
                    id='comp_division_dropdown',
                    options=[{'label': d, 'value': d} for d in COMP_DIVISIONS],
                    style={'backgroundColor': BACKGROUND_COLOR_DARK},
                    clearable=False,
                    value=init_comp_division),
            ]),
            dbc.Col([
                html.Div(children='''
                    Select Sub-Division
                '''),

                dcc.Dropdown(
                    id='division_dropdown',
                    options=get_divisions(init_comp_division),
                    style={'backgroundColor': BACKGROUND_COLOR_DARK},
                    clearable=False,
                    value=init_division),
            ]),
            dbc.Col([
                html.Div(children='''
                    Region of Team
                    '''),
                dcc.Dropdown(
                    id='region_dropdown',
                    options=get_regions(init_comp_division, init_division),
                    style={'backgroundColor': BACKGROUND_COLOR_DARK},
                    clearable=False,
                    value='all')
            ])
        ])
    ], fluid=True),
    html.Hr(),
    dcc.Loading(
        id="loading-rankings",
        children=[html.Div([dcc.Graph(id='rankings_graph', figure=fig_rankings)])],
        type="circle",
    ),
    # html.Div([dcc.Graph(id='rankings_graph', figure=fig_rankings)]),
    html.H3(children='Use checkboxes in table to pick which teams to show', style={
            'textAlign': 'center', 'font-size': '18px'}),
    html.Div([dash_table.DataTable(
        id='ranking_table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_as_list_view=True,
        row_selectable="multi",
        sort_action='native',
        selected_rows=list(range(len(df))),
        fixed_rows={'headers': True, 'data': 0},
        style_header={'font-weight': 'bold',
                      'font-size': '18px',
                      'backgroundColor': BACKGROUND_COLOR_DARK},
        style_table={
            'maxHeight': '300px',
            'overflowY': 'auto',
        },
        style_cell={'textAlign': 'center', 'width': '25%'},
        style_data_conditional=[
            {
                'if': {'column_id': 'Team'},
                'textAlign': 'left'
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': BACKGROUND_COLOR_LIGHT
            },
            {
                'if': {'row_index': 'even'},
                'backgroundColor': PLOT_BACKGROUND_COLOR
            }
        ]
    )]),
    html.Button('Select/Un-Select All', id='select-all-button', style={'backgroundColor': BACKGROUND_COLOR_DARK}),
    html.Hr(),
    dcc.Loading(
        id="loading-spirit",
        children=[html.Div([dcc.Graph(id='spirit_graph', figure=fig_spirit)])],
        type="circle",
    )
    # html.Div([dcc.Graph(id='spirit_graph', figure=fig_spirit)])
])


@app.callback([Output('division_dropdown', 'options'),
               Output('division_dropdown', 'value')],
              [Input('comp_division_dropdown', 'value')])
def update_division_dropdown(comp_division):
    div_options = get_divisions(comp_division)
    return div_options, div_options[0]['value']


@app.callback([Output('region_dropdown', 'options'),
               Output('region_dropdown', 'value')],
              [Input('comp_division_dropdown', 'value'), Input('division_dropdown', 'value')])
def update_region_dropdown(comp_division, division):
    region_options = get_regions(comp_division, division)
    return region_options, region_options[0]['value']


@app.callback(Output('ranking_table', 'data'),
              [Input('comp_division_dropdown', 'value'),
               Input('division_dropdown', 'value'),
               Input('region_dropdown', 'value')])
def update_table(comp_division, division, region):
    table_df = table_data(comp_division, division, region)
    return table_df.to_dict('records')


@app.callback(
    Output('ranking_table', "selected_rows"),
    [Input('select-all-button', 'n_clicks'),
     Input('ranking_table', "derived_virtual_data")]
)
def select_all(n_clicks, data):
    if data is None:
        return []
    if n_clicks is None:
        n_clicks = 0
    if n_clicks % 2 == 1:
        return []
    else:
        return [i for i in range(len(data))]


@app.callback(Output('rankings_graph', 'figure'),
              [Input('comp_division_dropdown', 'value'),
               Input('division_dropdown', 'value'),
               Input('region_dropdown', 'value'),
               Input('ranking_table', 'derived_virtual_selected_rows')],
              [State('ranking_table', 'derived_virtual_data')])
def update_ranking_figure(comp_division, division, region, rows, data):
    if (not data) or (not rows):
        teams = []
    else:
        teams = [t['Team'] for i, t in enumerate(data) if i in rows]
    new_ranking = ranking_data(comp_division, division, region, teams)
    return new_ranking


@app.callback(
    Output('spirit_graph', 'figure'),
    [Input('comp_division_dropdown', 'value'),
     Input('division_dropdown', 'value'),
     Input('region_dropdown', 'value'),
     Input('ranking_table', 'derived_virtual_selected_rows')],
    [State('ranking_table', 'derived_virtual_data')])
def update_spirit_figure(comp_division, division, region, rows, data):
    if (not data) or (not rows):
        teams = []
    else:
        teams = [t['Team'] for i, t in enumerate(data) if i in rows]
    new_spirit = spirit_correlation(comp_division, division, region, teams)
    return new_spirit


if __name__ == '__main__':
    app.run_server(debug=True)
