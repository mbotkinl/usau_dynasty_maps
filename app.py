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
    PLOT_BACKGROUND_COLOR, HEADER_2_SIZE, BACKGROUND_LIGHT_RGB, BACKGROUND_ALPHA, INITIAL_NUM_CHECKED

style = {'backgroundColor': BACKGROUND_COLOR_LIGHT, 'font-family': 'Arial'}

# todo: combine regions?
# todo: add cool filters to look at?

TITLE = 'USA Ultimate Nationals Explorer'
external_stylesheets = [dbc.themes.FLATLY]
META = [
    # A description of the app, used by e.g.
    # search engines when displaying search results.
    {
        'name': TITLE,
        'content': TITLE
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
app.title = TITLE
server = app.server

TURF_LINE_IMAGE = app.get_asset_url('grass.jpg')
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
            html.P(children=TITLE,
                   style={'textAlign': 'center', 'font-weight': 'bold', 'color': 'black',
                          'font-size': '65px', 'vertical-align': 'middle',
                          'padding': 10
                          }),
            html.Hr(style={'width': '50%', 'border': '4px solid black'}),
            html.Div([], style={'padding': 10})
        ], style={'backgroundColor': f'rgba{BACKGROUND_LIGHT_RGB + (BACKGROUND_ALPHA,)}',
                  'margin-left': '300px', 'margin-right': '300px', 'padding': 10, 'vertical-align': 'middle'}),
        html.Div([], style={'padding': 150}),
        html.Div([
            html.Div([
                html.H2('About The Project'),
                html.P(
                    children=['As a frisbee player, I was interested to see the rise and fall of teams in each region '
                              'over the years. To get a better sense of the ultimate frisbee dynasties and other '
                              'fun stats, I scraped data from the ',
                              html.A('USAU Archives', href='https://www.usaultimate.org/archives/', target="_blank",
                                     style={'color': BACKGROUND_COLOR_DARK}),
                              ' of nationals and then built this dashboard.'], style={'font-size': TEXT_SIZE}),
                html.Br(),
                html.H2('How To Use:'),
                html.Ul(children=[
                    html.Li('Use the filters to pick a division, a sub-division, and a region.'),
                    html.Li(
                        'Use checkboxes in the table to pick which teams to show in the graphs.'),
                    html.Li('Hover over or click on data points in graphs for more information.')
                ], style={'font-size': TEXT_SIZE}),
                html.Br(),
                html.H2('Notes'),
                html.Ul(children=[
                    html.Li('Divisions are named based on current USAU naming except in the case of college where'
                            ' there are separate sub divisions for before and after the DI/DIII separation.'),
                    html.Li('Where possible, historical regions for teams are updated to the region they currently play'
                            ' in. However, due to regional boundary redrawing, the regions of teams may change over the'
                            ' years.'),
                    html.Li('From 2000-2013, spirit scores were on a 1-5 scale. After 2013, the WFDF system of 0-20 was'
                            ' adopted. The scores from 2013 and before have been linearly scaled to the WFDF system.')
                ], style={'font-size': TEXT_SIZE}),
                html.Br(),
                html.P(children=
                       ['Questions/comments? Feel free to reach out on ',
                        html.A('LinkedIn', href='https://www.linkedin.com/in/micahbotkinlevy/', target="_blank",
                               style={'color': BACKGROUND_COLOR_DARK}),
                        ' or ',
                        html.A('Github', href='https://github.com/mbotkinl/usau_dynasty_maps', target="_blank",
                               style={'color': BACKGROUND_COLOR_DARK}), '.'
                        ],
                       style={'font-size': TEXT_SIZE}),
            ], style={'margin-left': '20px', 'margin-right': '20px'}),
        ],
            style={'backgroundColor': f'rgba{BACKGROUND_LIGHT_RGB + (BACKGROUND_ALPHA,)}',
                   'margin-left': '40px', 'margin-right': '40px', 'padding': 20, 'vertical-align': 'middle'}),
        html.Div([], style={'padding': 150}),
    ],
        style={'background-image': f'url({TURF_LINE_IMAGE})',
               'background-attachment': 'fixed',
               'background-position': 'center center',
               'background-repeat': 'no-repeat',
               'background-size': 'cover',
               }),

    # subsetting section
    html.Div([
        html.H2(children='SELECT FILTERS', style={'textAlign': 'center', 'padding': 1, 'font-weight': 'bold',
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
                              }),
        html.Div([], style={'padding': 10}),
    ], style={'padding': 80,
              'backgroundColor': BACKGROUND_COLOR_DARK
              }),

    # table section
    html.Div([
        html.H2(children='NATIONALS SUMMARY BY TEAM', style={'textAlign': 'center', 'padding': 1,
                                                             'font-size': HEADER_2_SIZE, 'letter-spacing': '1px'}),
        html.Div([], style={'padding': 30}),
        dcc.Loading(
            id="loading-table",
            children=[html.Div([dash_table.DataTable(
                id='ranking_table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                # style_as_list_view=True,
                row_selectable="multi",
                sort_action='native',
                selected_rows=list(range(INITIAL_NUM_CHECKED)),
                fixed_rows={'headers': True, 'data': 0},
                style_header={'font-weight': 'bold',
                              'font-size': TEXT_SIZE,
                              'backgroundColor': BACKGROUND_COLOR_LIGHT},
                style_table={
                    'maxHeight': '500px',
                    'overflowY': 'auto',
                },
                style_cell={'textAlign': 'center',
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
            )], style={'padding': 1})],
            type="circle",
        ),
        html.Div([html.Button('Select/Un-Select All', id='select-all-button',
                              style={'backgroundColor': BACKGROUND_COLOR_LIGHT})],
                 style={'padding': 20, 'font-size': TEXT_SIZE}),
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
        html.H3(children='Bubble size corresponds to number of appearances with reported spirit score',
                style={'textAlign': 'center', 'font-size': TEXT_SIZE}),
        dcc.Loading(
            id="loading-spirit",
            children=[html.Div([dcc.Graph(id='spirit_graph', figure=fig_spirit)])],
            type="circle",
        ),

    ], style={'padding': 10}),

    # Footer section
    html.Div([html.P(children=['©2019 by Micah Botkin-Levy.  ',
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
                                   style={'align': 'center'})
                               ])],
             style={'textAlign': 'right', 'padding': 10, 'backgroundColor': BACKGROUND_COLOR_DARK, 'color': 'white',
                    'font-size': '16px'}),
    # Hidden div inside the app that stores the intermediate value
    html.Div(id='table-length-value', children=len(df), style={'display': 'none'})
])


@app.callback([Output('division_dropdown', 'options'),
               Output('division_dropdown', 'value')],
              [Input('comp_division_dropdown', 'value')])
def update_division_dropdown(comp_division):
    div_options = get_divisions(comp_division)
    if 'D-I Women\'s' in [f['value'] for f in div_options]:
        value = 'D-I Women\'s'
    else:
        value = div_options[1]['value']

    return div_options, value


@app.callback([Output('region_dropdown', 'options'),
               Output('region_dropdown', 'value')],
              [Input('comp_division_dropdown', 'value'), Input('division_dropdown', 'value')])
def update_region_dropdown(comp_division, division):
    region_options = get_regions(comp_division, division)
    return region_options, region_options[0]['value']


@app.callback([Output('ranking_table', 'data'),
               Output('select-all-button', 'n_clicks'),
               Output('table-length-value', 'children')],
              [Input('comp_division_dropdown', 'value'),
               Input('division_dropdown', 'value'),
               Input('region_dropdown', 'value')])
def update_table(comp_division, division, region):
    table_df = table_data(comp_division, division, region)
    return table_df.to_dict('records'), 0, len(table_df)


@app.callback(
    Output('ranking_table', "selected_rows"),
    [Input('select-all-button', 'n_clicks'),
     Input('table-length-value', "children")]
)
def select_all(n_clicks, data_length):
    if data_length == 0:
        return []
    if n_clicks is None:
        n_clicks = 0
    if n_clicks == 0:
        return list(range(min(INITIAL_NUM_CHECKED, data_length)))
    elif n_clicks % 2 == 0:
        return []
    else:
        return list(range(data_length))


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
