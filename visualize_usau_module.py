import plotly.graph_objects as go
import pandas as pd

data = pd.read_csv('./data/national_data.csv')

DIVISIONS = data.division.unique()
REGIONS = data.Region.unique()

TOP_NUM = 4


def ranking_data(division, region='all'):
    if region == 'all':
        div_df = data[(data.division == division)].copy()
    else:
        div_df = data[(data.division == division) & (data.Region == region)].copy()

    plot_data = [go.Scatter(x=div_df[div_df.Team == t]['year'],
                            y=div_df[div_df.Team == t]['Standing'],
                            name=t) for t in div_df.Team.unique()]

    layout = {'title': 'Club Nationals Placement',
              'xaxis': {'title': 'Year'},
              'yaxis': {'autorange': 'reversed', 'zeroline': False, 'title': 'Nationals Placement',
                        'range': [1, max(div_df['Standing'])]}}  # todo: fix range

    return dict(data=plot_data, layout=layout)


def appearance_hist(division, region='all'):
    # todo: sync colors
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
