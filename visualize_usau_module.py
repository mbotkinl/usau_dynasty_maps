import plotly.graph_objects as go
import pandas as pd

data = pd.read_csv('./data/national_data.csv')

# clean up a bit
# TODO: typos in regions


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

    layout = {'title': 'Dash Data Visualization',
              'yaxis': {'autorange': 'reversed'}}

    return dict(data=plot_data, layout=layout)
#
# for i, (div, div_df) in enumerate(data.groupby('division')):
#
#     # histogram of appearances
#     appearances = div_df.Team.value_counts()
#     hist_data = div_df[div_df.Team.isin(appearances[appearances > 4].index.values)]
#     fig = go.Figure(data=[go.Histogram(x=hist_data.Team)]).update_xaxes(categoryorder='total descending')
#     plotly.offline.plot(fig, filename=f'national_appearances_{div}.html')
#
#     # national ranking plot
#     # div_df = data[(data.division=='MENS') & (data.Region=='Northeast')].copy()
#     plot_data = [go.Scatter(x=div_df[div_df.Team == t]['year'],
#                             y=div_df[div_df.Team == t]['Standing'],
#                             name=t) for t in div_df.Team.unique()]
#
#     fig = go.Figure(data=plot_data)
#     fig.update_yaxes(autorange="reversed", showgrid=False, zeroline=False)
#     fig.update_xaxes(showgrid=False)
#     plotly.offline.plot(fig, filename=f'national_ranking_{div}.html')
