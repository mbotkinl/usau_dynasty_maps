import plotly.graph_objects as go
import pandas as pd
import numpy as np

data = pd.read_csv('./data/national_data.csv')

TOP_NUM = 4


# TODO: change hover and click behavoir
# TODO: sync colors

COMP_DIVISIONS = data.comp_division.unique()


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


# def ranking_data(comp_division, division, region='all', highlight_curve=None):
def ranking_data(comp_division, division, region='all'):
    div_df = subset_df(comp_division, division, region)
    if div_df.empty:
        return {}
    # div_df['opacity'] = 1
    # if highlight_curve:
    #     div_df['opacity'] = 0.3
    #     div_df.loc[highlight_curve, 'opacity'] = 1

    plot_data = [go.Scatter(x=div_df[div_df.Team == t]['year'],
                            y=div_df[div_df.Team == t]['Standing'],
                            # opacity=div_df[div_df.Team == t]['opacity'].iloc[0],
                            hoverinfo='name',
                            name=t) for t in div_df.Team.unique()]

    layout = {'title': 'Nationals Placement',
              'hovermode': 'closest',
              'xaxis': {'title': 'Year'},
              'yaxis': {'autorange': 'reversed', 'zeroline': False, 'title': 'Nationals Placement'}}
                        # 'range': [1, max_placement]}}  # todo: fix range

    return dict(data=plot_data, layout=layout)


def appearance_hist(comp_division, division, region='all'):
    div_df = subset_df(comp_division, division, region)
    if div_df.empty:
        return {}
    appearances = div_df.Team.value_counts()
    hist_data = div_df[div_df.Team.isin(appearances[appearances > TOP_NUM].index.values)]
    if hist_data.empty:
        return {}
    plot_data = [go.Histogram(x=hist_data.Team)]
    layout = {'title': 'Most Nationals Appearances',
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
                            marker_size=df['count'] * 2,
                            hoverinfo='text',
                            hovertext=df.index,
                            mode='markers')]

    layout = {'title': 'Spirit Score to Placement Correlation',
              'xaxis': {'title': 'Average Spirit Score'},
              'yaxis': {'autorange': 'reversed', 'zeroline': False, 'title': 'Average Nationals Placement'}}
                        # 'range': [1, max(div_df['Standing'])]}}  # todo: fix range

    return dict(data=plot_data, layout=layout)
