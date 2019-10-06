import plotly.graph_objects as go
import pandas as pd
import numpy as np

data = pd.read_csv('./data/national_data.csv')

DIVISIONS = data.division.unique()
REGIONS = data.Region.unique()

TOP_NUM = 4

# TODO: change hover and click behavoir
# TODO: sync colors


# def ranking_data(division, region='all', highlight_curve=None):
def ranking_data(division, region='all'):
    if region == 'all':
        div_df = data[(data.division == division)].copy()
    else:
        div_df = data[(data.division == division) & (data.Region == region)].copy()

    # div_df['opacity'] = 1
    # if highlight_curve:
    #     div_df['opacity'] = 0.3
    #     div_df.loc[highlight_curve, 'opacity'] = 1

    plot_data = [go.Scatter(x=div_df[div_df.Team == t]['year'],
                            y=div_df[div_df.Team == t]['Standing'],
                            # opacity=div_df[div_df.Team == t]['opacity'].iloc[0],
                            hoverinfo='name',
                            name=t) for t in div_df.Team.unique()]

    layout = {'title': 'Club Nationals Placement',
              'hovermode': 'closest',
              'xaxis': {'title': 'Year'},
              'yaxis': {'autorange': 'reversed', 'zeroline': False, 'title': 'Nationals Placement',
                        'range': [1, max(div_df['Standing'])]}}  # todo: fix range

    return dict(data=plot_data, layout=layout)


def appearance_hist(division, region='all'):
    if region == 'all':
        div_df = data[(data.division == division)].copy()
    else:
        div_df = data[(data.division == division) & (data.Region == region)].copy()
    appearances = div_df.Team.value_counts()
    hist_data = div_df[div_df.Team.isin(appearances[appearances > TOP_NUM].index.values)]
    plot_data = [go.Histogram(x=hist_data.Team)]
    layout = {'title': 'Most Nationals Appearances',
              'yaxis': {'title': 'Number of Nationals Appearance'},
              'xaxis': {'title': 'Team',
                        'categoryorder': 'total descending'}}
    return dict(data=plot_data, layout=layout)


def spirit_correlation(division, region='all'):
    if region == 'all':
        div_df = data[(data.division == division)].copy()
    else:
        div_df = data[(data.division == division) & (data.Region == region)].copy()

    df = div_df.groupby('Team').agg(count=('year', 'count'),
                                    avg_spirit=('Spirit Scores', np.nanmean),
                                    avg_rank=('Standing', np.nanmean)
                                    )
    df = df[pd.notna(df.avg_spirit)]
    plot_data = [go.Scatter(x=df['avg_spirit'],
                            y=df['avg_rank'],
                            marker_size=df['count'] * 2,
                            hoverinfo='text',
                            hovertext=df.index,
                            mode='markers')]

    layout = {'title': 'Spirit Score to Placement Correlation',
              'xaxis': {'title': 'Average Spirit Score'},
              'yaxis': {'autorange': 'reversed', 'zeroline': False, 'title': 'Average Nationals Placement',
                        'range': [1, max(div_df['Standing'])]}}  # todo: fix range

    return dict(data=plot_data, layout=layout)
