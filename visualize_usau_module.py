import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS
import pandas as pd
import numpy as np

# import plotly.io as pio
# pio.templates.default = "plotly_dark"

TEMPLATE = 'plotly_dark'

data = pd.read_csv('./data/national_data.csv')

COMP_DIVISIONS = data.comp_division.unique()

# TODO: work on theme

PLOT_BACKGROUND_COLOR = '#FDFDFF'
BACKGROUND_COLOR_LIGHT = '#C6C5B9'
BACKGROUND_COLOR_DARK = '#62929E'

# https://www.w3schools.com/colors/colors_picker.asp
# https://coolors.co/ffbe0b-fb5607-ff006e-8338ec-3a86ff


# decent theme
# PLOT_BACKGROUND_COLOR = '#BFBFBF'
# BACKGROUND_COLOR_LIGHT = '#96939B'
# BACKGROUND_COLOR_DARK = '#564256'

# purples
# PLOT_BACKGROUND_COLOR = '#e0e0eb'
# BACKGROUND_COLOR_LIGHT = '#b3b3cc'
# BACKGROUND_COLOR_DARK = '#9494b8'

# grays
# PLOT_BACKGROUND_COLOR = '#f0f0f0'
# BACKGROUND_COLOR_LIGHT = '#cccccc'
# BACKGROUND_COLOR_DARK = '#808080'

AXIS_TITLE_SIZE = 18


# AXIS_TICK_SIZE = 18


def get_divisions(comp_division):
    divisions = data[data.comp_division == comp_division].division.unique()
    return [{'label': d, 'value': d} for d in divisions]


def get_regions(comp_division, division):
    regions = subset_df(comp_division, division, 'all').Region.unique()
    return [{'label': 'All Regions', 'value': 'all'}] + [{'label': r, 'value': r} for r in regions]


def subset_df(comp_division, division, region):
    if region == 'all':
        div_df = data[(data.comp_division == comp_division) & (data.division == division)].copy()
    else:
        div_df = data[
            (data.comp_division == comp_division) & (data.division == division) & (data.Region == region)].copy()
    return div_df


def table_data(comp_division, division, region='all'):
    div_df = subset_df(comp_division, division, region)
    if div_df.empty:
        return pd.DataFrame()
    # table_df = div_df.groupby(['Region', 'Team']).agg(num_appearances=('year', 'count'),
    table_df = div_df.groupby(['Team']).agg(num_appearances=('year', 'count'),
                                            avg_place=('Standing', 'mean'),
                                            avg_spirit=('SpiritScores', pd.np.nanmean)).reset_index()
    table_df = table_df.round(2)
    table_df = table_df.sort_values('num_appearances', ascending=False)
    table_df = table_df.rename(columns={'num_appearances': 'Number of Appearances',
                                        'avg_place': 'Average Placement',
                                        'avg_spirit': 'Average Spirit Score'})
    return table_df


def ranking_data(comp_division, division, region='all', highlight_teams=None):
    layout = {'hovermode': 'closest',
              'height': 740,
              'legend': {'orientation': 'v', 'itemclick': 'toggleothers', 'itemdoubleclick': False, 'x': 1},
              # 'xaxis': {'title': 'Year'},
              'paper_bgcolor': 'rgba(0,0,0,0)',
              'plot_bgcolor': PLOT_BACKGROUND_COLOR,
              'margin': {'t': 0},
              'xaxis': {'fixedrange': True},
              'yaxis': {'autorange': 'reversed', 'zeroline': False, 'fixedrange': True,
                        'title': {'text': 'Nationals Placement', 'font': {'size': AXIS_TITLE_SIZE}}}}

    div_df = subset_df(comp_division, division, region)
    if highlight_teams is None:
        highlight_teams = div_df.Team.tolist()
    if div_df.empty:
        return {'data': [], 'layout': layout}
    min_year = div_df.year.min()
    max_year = div_df.year.max()
    plot_data = []
    appearances = div_df.Team.value_counts()
    for t in appearances.keys():
        if t in highlight_teams:
            opacity = 1
            hover_info = 'y+name'
        else:
            opacity = 0.05
            hover_info = 'skip'
        team_df = div_df[div_df.Team == t].copy()
        team_df.set_index('year', inplace=True)
        team_df = team_df.reindex(list(range(min_year, max_year + 1)), fill_value=None)
        plot_data.append(go.Scatter(x=team_df.index,
                                    y=team_df['Standing'],
                                    hoverinfo=hover_info,
                                    mode='lines+markers',
                                    connectgaps=False,
                                    opacity=opacity,
                                    line={'shape': 'spline', 'smoothing': 0.3},
                                    marker={'size': 8},
                                    showlegend=False,
                                    name=t))

    # 'range': [1, max(div_df['Standing'])]}
    # print('data for ranking', plot_data)
    return dict(data=plot_data, layout=layout)


def spirit_correlation(comp_division, division, region='all', highlight_teams=None):
    layout = {
        # 'template': TEMPLATE,
        'paper_bgcolor': BACKGROUND_COLOR_LIGHT,
        'plot_bgcolor': PLOT_BACKGROUND_COLOR,
        'showlegend': False,
        'height': 550,
        'margin': {'t': 0},
        'xaxis': {'title': {'text': 'Average Spirit Score', 'font': {'size': AXIS_TITLE_SIZE}},
                  'fixedrange': True},
        'yaxis': {'autorange': 'reversed', 'zeroline': False, 'fixedrange': True,
                  'title': {'text': 'Average Nationals Placement', 'font': {'size': AXIS_TITLE_SIZE}}
                  }
    }

    div_df = subset_df(comp_division, division, region)
    if div_df.empty:
        return {'data': [], 'layout': layout}

    plot_data = []
    if highlight_teams is None:
        highlight_teams = div_df.Team.tolist()

    if highlight_teams:
        df = div_df[div_df['Team'].isin(highlight_teams)]. \
            groupby('Team').agg(count=('year', 'count'),
                                avg_spirit=('SpiritScores', np.nanmean),
                                avg_rank=('Standing', np.nanmean))
        df = df[pd.notna(df.avg_spirit)]
        if not df.empty:
            plot_data += [go.Scatter(x=df['avg_spirit'],
                                     y=df['avg_rank'],
                                     marker_size=df['count'] + 6,
                                     marker_color=BACKGROUND_COLOR_DARK,
                                     hoverinfo='text',
                                     hovertext=df.index.values +
                                               '<br><sub>Apperances with reported spirit: ' + df['count'].astype(
                                         str).values + '</sub>' +
                                               '<br><sub>Average spirit score: ' + np.round(df['avg_spirit'],
                                                                                            decimals=2).astype(
                                         str).values + '</sub>' +
                                               '<br><sub>Average placement: ' + np.round(df['avg_rank'],
                                                                                         decimals=2).astype(
                                         str).values + '</sub>'
                                     ,
                                     mode='markers')]
    if any(~div_df['Team'].isin(highlight_teams)):
        df_clear = div_df[~div_df['Team'].isin(highlight_teams)]. \
            groupby('Team').agg(count=('year', 'count'),
                                avg_spirit=('SpiritScores', np.nanmean),
                                avg_rank=('Standing', np.nanmean))
        df_clear = df_clear[pd.notna(df_clear.avg_spirit)]
        if not df_clear.empty:
            plot_data += [go.Scatter(x=df_clear['avg_spirit'],
                                     y=df_clear['avg_rank'],
                                     marker_size=df_clear['count'] + 6,
                                     marker_color=BACKGROUND_COLOR_DARK,
                                     hoverinfo='text',
                                     opacity=0.2,
                                     mode='markers')]
    if not plot_data:
        plot_data = []


    # 'range': [1, max(div_df['Standing'])]}
    # print('data for spirit', plot_data)

    return dict(data=plot_data, layout=layout)
