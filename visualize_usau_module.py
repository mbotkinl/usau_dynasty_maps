import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash_constants import BACKGROUND_COLOR_DARK, BACKGROUND_COLOR_LIGHT, PLOT_BACKGROUND_COLOR, AXIS_TITLE_SIZE, \
    TICK_SIZE

data = pd.read_csv('./data/national_data.csv')

COMP_DIVISIONS = data.comp_division.unique()


def get_divisions(comp_division: str) -> list:
    """ Get list of gendered sub divisions from competitive division

    Args:
        comp_division (str): competitive division name

    Returns:
        list

    """
    divisions = data[data.comp_division == comp_division].division.unique()
    return [{'label': d, 'value': d} for d in divisions]


def get_regions(comp_division: str, division: str) -> list:
    """ Get list of regions from competitive division and sub division name

    Args:
        comp_division (str): competitive division name
        division (str): gendered sub division name

    Returns:
        list
    """
    regions = subset_df(comp_division, division, 'all').Region.unique()
    return [{'label': 'All Regions', 'value': 'all'}] + [{'label': r, 'value': r} for r in regions]


def subset_df(comp_division: str, division: str, region: str) -> pd.DataFrame:
    """ Subset all results df using subset parameters

    Args:
        comp_division (str): competitive division name
        division (str): gendered sub division name
        region (str): region name

    Returns:
        pd.DataFrame
    """
    if region == 'all':
        div_df = data[(data.comp_division == comp_division) & (data.division == division)].copy()
    else:
        div_df = data[
            (data.comp_division == comp_division) & (data.division == division) & (data.Region == region)].copy()
    return div_df


def table_data(comp_division: str, division: str, region: str = 'all') -> pd.DataFrame:
    """ Get summary table from subset parameters

    Args:
        comp_division (str): competitive division name
        division (str): gendered sub division name
        region (str): region name

    Returns:
        pd.DataFrame
    """
    div_df = subset_df(comp_division, division, region)
    if div_df.empty:
        return pd.DataFrame()
    table_df = div_df.groupby(['Team']).agg(num_appearances=('year', 'count'),
                                            avg_place=('Standing', 'mean'),
                                            avg_spirit=('SpiritScores', pd.np.nanmean)).reset_index()
    table_df = table_df.round(2)
    table_df = table_df.sort_values('num_appearances', ascending=False)
    table_df = table_df.rename(columns={'num_appearances': 'Appearances',
                                        'avg_place': 'Average Placement',
                                        'avg_spirit': 'Average Spirit Score'})
    return table_df


def ranking_data(comp_division: str, division: str, region: str = 'all', highlight_teams: list = None) -> dict:
    """ Prepare placement scatter plot

    Args:
        comp_division (str): competitive division name
        division (str): gendered sub division name
        region (str): region name
        highlight_teams (list): list of teams to highlight

    Returns:
        dict
    """
    layout = {'hovermode': 'closest',
              'height': 740,
              'legend': {'orientation': 'v', 'itemclick': 'toggleothers', 'itemdoubleclick': False, 'x': 1},
              'paper_bgcolor': 'rgba(0,0,0,0)',
              'plot_bgcolor': PLOT_BACKGROUND_COLOR,
              'margin': {'t': 0},
              'font': {'size': TICK_SIZE, 'family': 'Arial'},
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
            hover_template = '<b>Team: %{fullData.name}</b><br>Year: %{x}<br>Placement: %{y}<extra></extra>'
        else:
            opacity = 0.05
            hover_template = ''
        team_df = div_df[div_df.Team == t].copy()
        team_df.set_index('year', inplace=True)
        team_df = team_df.reindex(list(range(min_year, max_year + 1)), fill_value=None)
        plot_data.append(go.Scatter(x=team_df.index,
                                    y=team_df['Standing'],
                                    # hoverinfo=hover_info,
                                    hoverinfo='skip',
                                    hovertemplate=hover_template,
                                    mode='lines+markers',
                                    connectgaps=False,
                                    opacity=opacity,
                                    line={'shape': 'spline', 'smoothing': 0.3},
                                    marker={'size': 8},
                                    showlegend=False,
                                    name=t))

    return dict(data=plot_data, layout=layout)


def spirit_correlation(comp_division: str, division: str, region: str = 'all', highlight_teams: list = None) -> dict:
    """ Prepare spirit scatter plot

    Args:
        comp_division (str): competitive division name
        division (str): gendered sub division name
        region (str): region name
        highlight_teams (list): list of teams to highlight

    Returns:
        dict
    """
    layout = {
        # 'template': TEMPLATE,
        'paper_bgcolor': BACKGROUND_COLOR_LIGHT,
        'plot_bgcolor': PLOT_BACKGROUND_COLOR,
        'showlegend': False,
        'height': 550,
        'margin': {'t': 0},
        'font': {'size': TICK_SIZE, 'family': 'Arial'},
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
                                     hoverlabel={'font': {'color': 'white'}},
                                     hoverinfo='text',
                                     hovertext='<b>Team: ' + df.index.values +
                                               '</b><br>Apperances with reported spirit: ' + df['count'].astype(
                                         str).values +
                                               '<br>Average spirit score: ' + np.round(df['avg_spirit'],
                                                                                            decimals=2).astype(
                                         str).values +
                                               '<br>Average placement: ' + np.round(df['avg_rank'],
                                                                                         decimals=2).astype(
                                         str).values
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
                                     opacity=0.1,
                                     mode='markers')]
    if not plot_data:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "No Spirit data found",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }

    return dict(data=plot_data, layout=layout)
