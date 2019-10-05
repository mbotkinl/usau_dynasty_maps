import plotly.graph_objects as go
import pandas as pd

data = pd.read_csv('./data/national_data.csv')

DIVISIONS = data.division.unique()
REGIONS = data.Region.unique()


def ranking_data(division, region='all'):
    if region == 'all':
        div_df = data[(data.division == division)].copy()
    else:
        div_df = data[(data.division == division) & (data.Region == region)].copy()

    plot_data = [go.Scatter(x=div_df[div_df.Team == t]['year'],
                            y=div_df[div_df.Team == t]['Standing'],
                            name=t) for t in div_df.Team.unique()]

    layout = {'title': 'Club Nationals Placement',
              'yaxis': {'autorange': 'reversed', 'zeroline': False,
                        'range': [1, max(div_df['Standing'])]}}  # todo: fix range

    return dict(data=plot_data, layout=layout)
