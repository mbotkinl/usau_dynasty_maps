# -*- coding: utf-8 -*-
import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from visualize_usau_module import ranking_data, spirit_correlation, \
    COMP_DIVISIONS, get_divisions, get_regions, table_data

from dash_constants import BACKGROUND_COLOR_DARK, BACKGROUND_COLOR_LIGHT, TEXT_SIZE, \
    PLOT_BACKGROUND_COLOR, HEADER_2_SIZE, BACKGROUND_LIGHT_RGB, BACKGROUND_ALPHA

style = {'backgroundColor': BACKGROUND_COLOR_LIGHT, 'font-family': 'Arial'}

# TODO: align fonts

external_stylesheets = [dbc.themes.FLATLY]
META = [
                    # A description of the app, used by e.g.
                    # search engines when displaying search results.
                    {
                        'name': 'USAU Data Project',
                        'content': 'USAU Data Project'
                    },
                    # A tag that tells Internet Explorer (IE)
                    # to use the latest renderer version available
                    # to that browser (e.g. Edge)
                    {
                        'http-equiv': 'X-UA-Compatible',
                        'content': 'IE=edge'
                    },
                    # A tag that tells the browser not to scale
                    # desktop widths to fit mobile screens.
                    # Sets the width of the viewport (browser)
                    # to the width of the device, and the zoom level
                    # (initial scale) to 1.
                    #
                    # Necessary for "true" mobile support.
                    # {
                    #     'name': 'viewport',
                    #     'content': 'width=device-width, initial-scale=0.4'
                    # }
                ]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=META
                )
app.title = 'USAU Data Project'
server = app.server

# TURF_LINE_IMAGE = app.get_asset_url('turf.jpg')
TURF_LINE_IMAGE = app.get_asset_url('grass.jpg')
GRASS_IMAGE = app.get_asset_url('grass.jpg')
LINKEDIN_IMAGE = app.get_asset_url('LinkedIn.png')
GITHUB_IMAGE = app.get_asset_url('GitHub.png')

init_comp_division = COMP_DIVISIONS[0]
init_division = get_divisions(init_comp_division)[1]['value']

df = table_data(init_comp_division, init_division)
fig_rankings = ranking_data(comp_division=init_comp_division, division=init_division, highlight_teams=df.Team.tolist())
fig_spirit = spirit_correlation(comp_division=init_comp_division, division=init_division)

app.layout = html.Div(style=style, children=[

    # title
    html.Div([
        html.Div([], style={'padding': 150}),
        html.Div([
            html.Div([], style={'padding': 10}),
            html.Hr(style={'width': '50%', 'border': '2px solid black'}),
            html.P(children='USA Ultimate Data Project', style={'textAlign': 'center', 'font-weight': 'bold', 'color': 'black',
                                                                      'font-size': '65px', 'vertical-align': 'middle',
                                                                      'padding': 10
                                                                      # 'position': 'absolute', 'top': '50%', 'width': '100%'
                                                                      }),
            html.Hr(style={'width': '50%', 'border': '4px solid black'}),
            html.Div([], style={'padding': 10})
        ], style={'backgroundColor': f'rgba{BACKGROUND_LIGHT_RGB + (BACKGROUND_ALPHA,)}',
                  'margin-left': '300px', 'margin-right': '300px', 'padding': 10, 'vertical-align': 'middle'}),
        html.Div([], style={'padding': 150}),
        html.Div([
            html.Div([
                html.H2('About the project'),
                html.P(children='As a frisbee player, I was interested to see the rise and fall of teams in each region over the years. '
                            'To get a better sense of the ultimate frisbee dynasties and other fun stats, I scraped data from the USAU '
                            'archives of nationals and then built this dashboard.', style={'font-size': TEXT_SIZE}),
                html.Br(),
                html.H2('How to use'),
                html.Ul(children=[
                    html.Li('Use the selection filters to pick a division, a sub-division, and a region'),
                    html.Li('Use checkboxes in the table to pick which teams to show in the graphs (updates automatically)'),
                    html.Li('Hover over or click on data points in graphs for more info')
                ], style={'font-size': TEXT_SIZE}),
                html.Br(),
                html.H2('Notes'),
                html.Ul(children=[
                    html.Li('Divisions are named based on current USAU naming except in the case of college where there are separate sub divisions for before and after the DI/DIII separation'),
                    html.Li('Due to regional boundary redrawing, the regional of teams change over the years')
                ], style={'font-size': TEXT_SIZE}),
                html.Br(),
                html.P('Questions/comments? Feel free to contact on LinkedIn or GitHub with the links at the bottom.',
                       style={'font-size': TEXT_SIZE}),
            ], style={'margin-left': '20px', 'margin-right': '20px'}),
        ],
            style={'backgroundColor': f'rgba{BACKGROUND_LIGHT_RGB + (BACKGROUND_ALPHA,)}',
                   'margin-left': '40px', 'margin-right': '40px', 'padding': 20, 'vertical-align': 'middle'}),
        html.Div([], style={'padding': 150}),
    ],
             style={'background-image': f'url({TURF_LINE_IMAGE})',
                                        # 'min-height': '20px',
                    # 'max-height': '1000px',
                    'background-attachment': 'fixed',
                    'background-position': 'center center',
                    'background-repeat': 'no-repeat',
                    'background-size': 'cover',
                    # 'height': '200vh',
                    # 'z-index': -1,
                    # 'background-clip': 'content-box	',
                    # 'overflow': 'hidden',

                                       }),

    # subsetting section
    html.Div([
        html.H2(children='SELECTION FILTERS', style={'textAlign': 'center', 'padding': 1, 'font-weight': 'bold',
                                                     'font-size': HEADER_2_SIZE, 'color': 'white',
                                                     'letter-spacing': '1px'}),
        html.Div([], style={'padding': 30}),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.P(children='Competitive Division', style={'color': 'white', 'font-size': TEXT_SIZE}),
                    dcc.Dropdown(
                        id='comp_division_dropdown',
                        options=[{'label': d, 'value': d} for d in COMP_DIVISIONS],
                        style={'backgroundColor': PLOT_BACKGROUND_COLOR, 'position': 'relative', 'zIndex': '999',
                               'font-size': TEXT_SIZE},
                        clearable=False,
                        value=init_comp_division),
                ]),
                dbc.Col([
                    html.P(children='Sub-Division', style={'color': 'white', 'font-size': TEXT_SIZE}),
                    dcc.Dropdown(
                        id='division_dropdown',
                        options=get_divisions(init_comp_division),
                        style={'backgroundColor': PLOT_BACKGROUND_COLOR, 'position': 'relative', 'zIndex': '999',
                               'font-size': TEXT_SIZE},
                        clearable=False,
                        value=init_division),
                ]),
                dbc.Col([
                    html.P(children='Region of Team', style={'color': 'white', 'font-size': TEXT_SIZE}),
                    dcc.Dropdown(
                        id='region_dropdown',
                        options=get_regions(init_comp_division, init_division),
                        style={'backgroundColor': PLOT_BACKGROUND_COLOR, 'position': 'relative', 'zIndex': '999',
                               'font-size': TEXT_SIZE},
                        clearable=False,
                        value='all')
                ])
            ])
        ], fluid=True, style={'padding': 1,
                              # 'backgroundColor': f'rgba{BACKGROUND_LIGHT_RGB + (BACKGROUND_ALPHA,)}'
                              }),
        html.Div([], style={'padding': 10}),
    ], style={'padding': 80,
              'backgroundColor': BACKGROUND_COLOR_DARK
              # 'background-image': f'url({TURF_LINE_IMAGE})',
              # 'min-height': '250px',
              # 'background-attachment': 'fixed',
              # 'background-position': 'center',
              # 'background-repeat': 'no-repeat',
              # 'background-size': 'cover',
              }),

    # table section
    html.Div([
        html.H2(children='TEAM SUMMARY TABLE', style={'textAlign': 'center', 'padding': 1,
                                                      'font-size': HEADER_2_SIZE, 'letter-spacing': '1px'}),
        html.Div([], style={'padding': 30}),
        html.Div([dash_table.DataTable(
            id='ranking_table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            # style_as_list_view=True,
            row_selectable="multi",
            sort_action='native',
            selected_rows=list(range(len(df))),
            fixed_rows={'headers': True, 'data': 0},
            style_header={'font-weight': 'bold',
                          'font-size': TEXT_SIZE,
                          'backgroundColor': BACKGROUND_COLOR_LIGHT},
            style_table={
                'maxHeight': '400px',
                'overflowY': 'auto',
                # 'maxWidth': '100px',
                # 'overflowX': 'auto',
            },
            # fill_width=False,
            style_cell={'textAlign': 'center',
                        # 'width': '25%',
                        'font-size': '20px',
                        'textOverflow': 'ellipsis',
                        'minWidth': '0px', 'maxWidth': '10px',
                        'font_family': 'Arial'},
            style_data_conditional=[
                {
                    'if': {'column_id': 'Team'},
                    'width': '18%',
                    'textAlign': 'left'
                },
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'white'
                },
                {
                    'if': {'row_index': 'even'},
                    'backgroundColor': PLOT_BACKGROUND_COLOR
                }
            ]
        )], style={'padding': 1}),
        html.Div([html.Button('Select/Un-Select All', id='select-all-button',
                              style={'backgroundColor': BACKGROUND_COLOR_LIGHT})],
                 style={'padding': 20,'font-size': TEXT_SIZE}),
    ], style={'backgroundColor': PLOT_BACKGROUND_COLOR, 'padding': 60}),


    # graph section
    html.Div([
        # placement graph
        html.H2(children='Nationals Placement by Year', style={'textAlign': 'center', 'padding': 10,
                                                               'font-size': HEADER_2_SIZE}),
        dcc.Loading(
            id="loading-rankings",
            children=[html.Div([dcc.Graph(id='rankings_graph', figure=fig_rankings)])],
            type="circle",
        ),

        # spirit graph
        html.H2(children='Spirit Score to Placement Correlation',
                style={'textAlign': 'center', 'padding': 10,
                       'font-size': HEADER_2_SIZE}),
        html.H3(children='Size corresponds to number of appearances with reported spirit score',
                style={'textAlign': 'center', 'font-size': TEXT_SIZE}),
        dcc.Loading(
            id="loading-spirit",
            children=[html.Div([dcc.Graph(id='spirit_graph', figure=fig_spirit)])],
            type="circle",
        ),

    ], style={'padding': 80}),

    # Footer section
    html.Div([html.P(children=['©2019 by Micah Botkin-Levy. ',
                               html.A([
                                   html.Img(
                                       src=LINKEDIN_IMAGE,
                                       style={
                                           'height': '3%',
                                           'width': '3%',
                                       }
                                   )
                               ], href='https://www.linkedin.com/in/micahbotkinlevy/', target="_blank"),
                               ' ',
                               html.A([
                                   html.Img(
                                       src=GITHUB_IMAGE,
                                       style={
                                           'height': '3%',
                                           'width': '3%',
                                       }
                                   )
                               ], href='https://github.com/mbotkinl/usau_dynasty_maps', target="_blank",
                                   style={'align': 'center'})])],
             style={'textAlign': 'right', 'padding': 20}),
])


@app.callback([Output('division_dropdown', 'options'),
               Output('division_dropdown', 'value')],
              [Input('comp_division_dropdown', 'value')])
def update_division_dropdown(comp_division):
    div_options = get_divisions(comp_division)
    return div_options, div_options[1]['value']


@app.callback([Output('region_dropdown', 'options'),
               Output('region_dropdown', 'value')],
              [Input('comp_division_dropdown', 'value'), Input('division_dropdown', 'value')])
def update_region_dropdown(comp_division, division):
    region_options = get_regions(comp_division, division)
    return region_options, region_options[0]['value']


@app.callback([Output('ranking_table', 'data'),
               Output('select-all-button', 'n_clicks')],
              [Input('comp_division_dropdown', 'value'),
               Input('division_dropdown', 'value'),
               Input('region_dropdown', 'value')])
def update_table(comp_division, division, region):
    table_df = table_data(comp_division, division, region)

    return table_df.to_dict('records'), 0


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
    # app.run_server(debug=True)
    server.run()
