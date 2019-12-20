import plotly.graph_objects as go
import pandas as pd
import numpy as np

data = pd.read_csv('./data/national_data.csv')

MAX_HIST = 12

# TODO: change hover and click behavoir
# TODO: sync colors

COMP_DIVISIONS = data.comp_division.unique()

BACKGROUND_COLOR = '#f0f0f0'


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
        return {}
    table_df = div_df.groupby('Team').agg(num_appearances=('year', 'count'),
                                          avg_place=('Standing', 'mean'),
                                          avg_spirit=('SpiritScores', pd.np.nanmean)).reset_index()
    table_df = table_df.round(2)
    table_df = table_df.sort_values('num_appearances', ascending=False)
    return table_df


# def ranking_data(comp_division, division, region='all', highlight_curve=None):
def ranking_data(comp_division, division, region='all', highlight_teams=None):
    div_df = subset_df(comp_division, division, region)
    if highlight_teams is None:
        highlight_teams = div_df.Team.tolist()
    if div_df.empty:
        return {}
    min_year = div_df.year.min()
    max_year = div_df.year.max()
    plot_data = []
    appearances = div_df.Team.value_counts()
    for t in appearances.keys():
        if t in highlight_teams:
            opacity = 1
        else:
            opacity = 0.05
        team_df = div_df[div_df.Team == t].copy()
        team_df.set_index('year', inplace=True)
        team_df = team_df.reindex(list(range(min_year, max_year + 1)), fill_value=None)
        plot_data.append(go.Scatter(x=team_df.index,
                                    y=team_df['Standing'],
                                    hoverinfo='y+name',
                                    mode='lines+markers',
                                    connectgaps=False,
                                    opacity=opacity,
                                    line={'shape': 'spline', 'smoothing': 0.7},
                                    marker={'size': 8},
                                    showlegend=False,
                                    name=t))

    layout = {'title': 'Nationals Placement',
              'hovermode': 'closest',
              'height': 900,
              'legend': {'orientation': 'v', 'itemclick': 'toggleothers', 'itemdoubleclick': False, 'x': 1},
              # 'xaxis': {'title': 'Year'},
              'plot_bgcolor': BACKGROUND_COLOR,
              'yaxis': {'autorange': 'reversed', 'zeroline': False, 'title': 'Nationals Placement'}}
    # 'range': [1, max_placement]}}  # todo: fix range

    return dict(data=plot_data, layout=layout)


def appearance_hist(comp_division, division, region='all'):
    div_df = subset_df(comp_division, division, region)
    if div_df.empty:
        return {}
    appearances = div_df.Team.value_counts()
    hist_data = div_df[div_df.Team.isin(appearances.iloc[0:min(len(appearances), MAX_HIST)].index.values)]
    if hist_data.empty:
        return {}
    plot_data = [go.Histogram(x=hist_data.Team,
                              hoverinfo='y')]
    layout = {'title': 'Most Nationals Appearances',
              'plot_bgcolor': BACKGROUND_COLOR,
              # 'template': TEMPLATE,
              'yaxis': {'title': 'Number of Nationals Appearance'},
              'xaxis': {'title': 'Team',
                        'categoryorder': 'total descending'}}
    return dict(data=plot_data, layout=layout)


def spirit_correlation(comp_division, division, region='all'):
    div_df = subset_df(comp_division, division, region)
    if div_df.empty:
        return {}
    df = div_df.groupby('Team').agg(count=('year', 'count'),
                                    avg_spirit=('SpiritScores', np.nanmean),
                                    avg_rank=('Standing', np.nanmean)
                                    )
    df = df[pd.notna(df.avg_spirit)]
    if df.empty:
        return {}
    plot_data = [go.Scatter(x=df['avg_spirit'],
                            y=df['avg_rank'],
                            marker_size=df['count'] + 6,
                            hoverinfo='text',
                            hovertext=df.index.values +
                                      '<br><sub>Apperances with reported spirit: ' + df['count'].astype(
                                str).values + '</sub>' +
                                      '<br><sub>Average spirit score: ' + np.round(df['avg_spirit'], decimals=2).astype(
                                str).values + '</sub>' +
                                      '<br><sub>Average placement: ' + np.round(df['avg_rank'], decimals=2).astype(
                                str).values + '</sub>'
                            ,
                            mode='markers')]

    # todo: subplot with size of dot
    layout = {
        'title': 'Spirit Score to Placement Correlation <br><sub>Size corresponds to number of appearances with reported spirit score</sub>',
        # 'template': TEMPLATE,
        'plot_bgcolor': BACKGROUND_COLOR,
        'xaxis': {'title': 'Average Spirit Score'},
        'yaxis': {'autorange': 'reversed', 'zeroline': False, 'title': 'Average Nationals Placement'}}
    # 'range': [1, max(div_df['Standing'])]}}  # todo: fix range

    return dict(data=plot_data, layout=layout)
