import math
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash_constants import BACKGROUND_COLOR_DARK, BACKGROUND_COLOR_LIGHT, PLOT_BACKGROUND_COLOR, AXIS_TITLE_SIZE, \
    TICK_SIZE

data = pd.read_csv('./data/national_data.csv')

COMP_DIVISIONS = data.comp_division.unique()


def ordinal(n: float) -> str:
    """ Convert number to ordinal number

    Args:
        n (float, int): number

    Returns:
        str: ordinal number
    """
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10::4])


def get_blank_plot(message: str) -> dict:
    """Generate blank plot with message

    Args:
        message (str): message to display

    Returns:
        plotly dict
    """
    return {
            "layout": {
                'paper_bgcolor': BACKGROUND_COLOR_LIGHT,
                'plot_bgcolor': PLOT_BACKGROUND_COLOR,
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": message,
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


def get_divisions(comp_division: str) -> list:
    """ Get list of gendered sub divisions from competitive division

    Args:
        comp_division (str): competitive division name

    Returns:
        list

    """
    divisions = data[data.comp_division == comp_division].division.unique()
    division_list = list(divisions)
    division_list.sort(key=lambda x: x[-1], reverse=True)
    return [{'label': d, 'value': d} for d in division_list]


def get_regions(comp_division: str, division: str) -> list:
    """ Get list of regions from competitive division and sub division name

    Args:
        comp_division (str): competitive division name
        division (str): gendered sub division name

    Returns:
        list
    """
    regions = subset_df(comp_division, division, 'all').Region.unique()
    region_list = list(regions)
    region_list.sort(key=lambda x: x[-1], reverse=True)
    return [{'label': 'All Regions', 'value': 'all'}] + [{'label': r, 'value': r} for r in region_list]


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
                                            avg_spirit=('SpiritScores', np.nanmean)).reset_index()
    table_df = table_df.round(2)
    table_df = table_df.sort_values('num_appearances', ascending=False)
    table_df = table_df.rename(columns={'num_appearances': 'Appearances',
                                        'avg_place': 'Avg Placement',
                                        'avg_spirit': 'Avg Spirit Score'})
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

    div_df = subset_df(comp_division, division, region)
    if highlight_teams is None:
        highlight_teams = div_df.Team.tolist()
    if div_df.empty:
        return get_blank_plot('No data found')
    min_year = div_df.year.min()
    max_year = div_df.year.max()
    max_standing = div_df['Standing'].max()
    plot_data = []

    for t in div_df['Team'].unique():
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
                                    hoverinfo='skip',
                                    hovertemplate=hover_template,
                                    mode='lines+markers',
                                    connectgaps=False,
                                    opacity=opacity,
                                    line={'shape': 'linear'},
                                    marker={'size': 18},
                                    showlegend=False,
                                    name=t))

    tickvals = list(reversed(range(1, max_standing + 1)))
    ticktext = [ordinal(n) for n in tickvals]
    extra_space = 0.5 if (max_year - min_year) > 15 else 0.2
    layout = {'hovermode': 'closest',
              'height': 740,
              'legend': {'orientation': 'v', 'itemclick': 'toggleothers', 'itemdoubleclick': False, 'x': 1},
              'paper_bgcolor': 'rgba(0,0,0,0)',
              'plot_bgcolor': PLOT_BACKGROUND_COLOR,
              'margin': {'t': 0},
              'font': {'size': TICK_SIZE, 'family': 'Arial'},
              'xaxis': {'fixedrange': True,
                        'tickformat': 'd',
                        'range': [min_year - extra_space, max_year + extra_space]},
              'yaxis': {'autorange': 'reversed', 'zeroline': False, 'fixedrange': True,
                        'title': {'text': 'Nationals Placement', 'font': {'size': AXIS_TITLE_SIZE}},
                        'tickmode': 'array', 'tickvals': tickvals, 'ticktext': ticktext,
                        }}
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

    div_df = subset_df(comp_division, division, region)
    if div_df.empty:
        return get_blank_plot('No data found')

    plot_data = []
    if highlight_teams is None:
        highlight_teams = div_df.Team.tolist()

    agg_team = div_df.groupby('Team').agg(count=('year', 'count'),
                                avg_spirit=('SpiritScores', np.nanmean),
                                avg_rank=('Standing', np.nanmean)).reset_index()
    if highlight_teams:
        df = agg_team[agg_team['Team'].isin(highlight_teams)]
        df = df[pd.notna(df.avg_spirit)]
        if not df.empty:
            plot_data += [go.Scatter(x=df['avg_spirit'],
                                     y=df['avg_rank'],
                                     marker_size=df['count']*1.5 + 10,
                                     marker_color=BACKGROUND_COLOR_DARK,
                                     hoverlabel={'font': {'color': 'white'}},
                                     hoverinfo='text',
                                     hovertext='<b>Team: ' + df['Team'].values +
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
        df_clear = agg_team[~agg_team['Team'].isin(highlight_teams)]
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
        return get_blank_plot('No Spirit data found')

    high_tick = int(np.floor(min(agg_team['avg_rank'])))
    low_tick = int(np.ceil(max(agg_team['avg_rank']))+1)
    tickvals = list(reversed(range(high_tick, low_tick)))
    ticktext = [ordinal(n) for n in tickvals]
    layout = {
        'paper_bgcolor': BACKGROUND_COLOR_LIGHT,
        'plot_bgcolor': PLOT_BACKGROUND_COLOR,
        'showlegend': False,
        'height': 550,
        'margin': {'t': 0},
        'font': {'size': TICK_SIZE, 'family': 'Arial'},
        'xaxis': {'title': {'text': 'Average Spirit Score', 'font': {'size': AXIS_TITLE_SIZE}},
                  'fixedrange': True},
        'yaxis': {'autorange': 'reversed', 'zeroline': False, 'fixedrange': True,
                  'title': {'text': 'Average Nationals Placement', 'font': {'size': AXIS_TITLE_SIZE}},
                  'tickmode': 'array', 'tickvals': tickvals, 'ticktext': ticktext,
                  }
    }
    return dict(data=plot_data, layout=layout)
