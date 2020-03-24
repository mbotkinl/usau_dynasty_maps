import numpy as np
import pandas as pd
from plotly.offline import plot
import plotly.express as px
import plotly.graph_objects as go
from visualize_usau_module import ordinal, PLOT_BACKGROUND_COLOR, TICK_SIZE, AXIS_TITLE_SIZE, BACKGROUND_COLOR_DARK, \
    BACKGROUND_COLOR_LIGHT


# TODO: use plotly templates

data = pd.read_csv('./data/national_data.csv')

############################################
# WOMXN BIG 4
############################################
BIG_4 = ['LADY GODIVA', 'FURY', 'RIOT', 'BRUTE SQUAD']
div_df = data[data['Team'].isin(BIG_4)].copy()
# min_year = div_df.year.min()
min_year = 1995
max_year = div_df.year.max()
max_standing = div_df['Standing'].max()
plot_data = []

for t in BIG_4:
    opacity = 1
    hover_template = '<b>Team: %{fullData.name}</b><br>Year: %{x}<br>Placement: %{y}<extra></extra>'
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
                                # showlegend=False,
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
                    'title': {'text': 'Year', 'font': {'size': AXIS_TITLE_SIZE}},
                    'range': [min_year - extra_space, max_year + extra_space]},
          'yaxis': {'autorange': 'reversed', 'zeroline': False, 'fixedrange': True,
                    'title': {'text': 'Nationals Placement', 'font': {'size': AXIS_TITLE_SIZE}},
                    'tickmode': 'array', 'tickvals': tickvals, 'ticktext': ticktext,
                    }}

plot(dict(data=plot_data, layout=layout), filename='womxn_big_4_ranks.html')


# top three finishes
start_year = 1999
top_3_finishes = len(div_df[(div_df['year'] >= start_year) & (div_df['Standing'] <= 3)])
percent_top_3 = top_3_finishes/((2019 - start_year + 1) * 3) * 100
print(percent_top_3)

# unique winners of nationals for mens
num_unique_mens_champs = data[(data['comp_division'] == 'Club') & (data['division'] == 'MENS') &
                              (data['Standing'] == 1) & (data['year'] >= start_year)]['Team'].nunique()
print(num_unique_mens_champs)


# spirit vs rank
spirit_vs_rank = div_df.groupby('Team').agg(count=('Team', 'count'),
                                            avg_rank=('Standing', 'mean'),
                                            avg_spirit=('SpiritScores', 'mean')).reset_index()
spirit_vs_rank['marker_size'] = spirit_vs_rank['count'] ** 3 / 1000
fig = px.scatter(spirit_vs_rank, 'avg_spirit', 'avg_rank', size='marker_size', text='Team')
high_tick = int(np.floor(min(spirit_vs_rank['avg_rank'])))
low_tick = int(np.ceil(max(spirit_vs_rank['avg_rank'])) + 1)
tickvals = list(reversed(range(high_tick, low_tick)))
ticktext = [ordinal(n) for n in tickvals]
layout = {
    'font': {'size': TICK_SIZE, 'family': 'Arial'},
    'xaxis': {'title': {'text': 'Average Spirit Score', 'font': {'size': AXIS_TITLE_SIZE}},
              'fixedrange': True},
    'yaxis': {'autorange': 'reversed', 'zeroline': False, 'fixedrange': True,
              'title': {'text': 'Average Nationals Placement', 'font': {'size': AXIS_TITLE_SIZE}},
              'tickmode': 'array', 'tickvals': tickvals, 'ticktext': ticktext,
              }
}
fig.update_layout(layout)
fig.update_traces(textposition='top center')
plot(fig, filename='spirit_vs_rank_big_4.html')


############################################
# change in spirit score over time
############################################
# DIV = 'Club'
DIV = 'College'

# spirit_year_region = data[data['comp_division'] == DIV'].groupby(['Region', 'division', 'year'])['SpiritScores'].mean().reset_index()
spirit_year_region = data[(data['comp_division'] == DIV) & (data['year'] > 2013)].groupby(['Region', 'division', 'year'])['SpiritScores'].mean().reset_index()
fig = px.scatter(spirit_year_region, 'year', 'SpiritScores', color='Region', facet_row="division")
plot(fig, filename='spirit_score_by_year.html')

spirit_year_region = data[(data['comp_division'] == DIV) & (data['year'] > 2013)].groupby(['division', 'year'])['SpiritScores'].mean().reset_index()
spirit_year_region = data[(data['comp_division'] == DIV)].groupby(['division', 'year'])['SpiritScores'].mean().reset_index()
# fig = px.scatter(spirit_year_region, 'year', 'SpiritScores', color="division", trendline='ols')
fig = px.scatter(spirit_year_region, 'year', 'SpiritScores', color="division")
plot(fig, filename='spirit_score_by_year_division.html')


data['pre_2013'] = 0
data.loc[data['year'] <= 2013, 'pre_2013'] = 1
fig = px.histogram(data, x='SpiritScores', color='pre_2013')
plot(fig)
############################################
# Regional plots
############################################

# avg ranking by region by year
# TODO: should include count
avg_rank_year_region = data[data['comp_division'] == 'Club'].groupby(['Region', 'division', 'year'])['Standing'].mean().reset_index()
fig = px.scatter(avg_rank_year_region, 'year', 'Standing', color='Region', facet_row="division")
plot(fig, filename='avg_standing_by_year_region.html')

# top ranking by region by year
# TODO: should include count
# TODO: why not all at least one 1?
max_rank_year_region = data[data['comp_division'] == 'Club'].groupby(['Region', 'division', 'year'])['Standing'].max().reset_index()
fig = px.scatter(max_rank_year_region, 'year', 'Standing', color='Region', facet_row="division")
fig.update_layout({'yaxis': {'autorange': 'reversed', 'zeroline': False, 'fixedrange': True}})
plot(fig, filename='max_standing_by_year_region.html')

# regional avg spirit score vs avg ranking
spirit_vs_rank_by_region = data[data['comp_division'] == 'Club'].groupby(['Region', 'division']).\
    agg(avg_rank=('Standing', 'mean'),
        avg_spirit=('SpiritScores', 'mean')).reset_index()
fig = px.scatter(spirit_vs_rank_by_region, 'avg_rank', 'avg_spirit', color='Region', facet_row="division")
plot(fig, filename='spirit_vs_rank_by_year_region.html')

# # regional avg spirit score vs avg ranking
# spirit_vs_rank_by_region = data[data['comp_division'] != 'Club'].groupby(['Region', 'division']).\
#     agg(avg_rank=('Standing', 'mean'),
#         avg_spirit=('SpiritScores', 'mean')).reset_index()
# fig = px.scatter(spirit_vs_rank_by_region, 'avg_rank', 'avg_spirit', color='Region', facet_row="division")
# plot(fig, filename='spirit_vs_rank_by_year_region_college.html')


##################################
# fun facts
##################################

# club team with most appearances but no wins
winning_teams = data[data['Standing'] == 1]['Team'].unique()
data[~data['Team'].isin(winning_teams)]['Team'].value_counts().iloc[0:10]

data[data['Team'] == 'Texas']


# worst spirit score
start_year = 2014
DIV = 'Club'
# DIV = 'College'
data[(data['year'] >= start_year) & (data['comp_division'] == DIV)].sort_values('SpiritScores').iloc[0:10]
data[(data['year'] >= start_year) & (data['comp_division'] == DIV)].sort_values('SpiritScores', ascending=False).iloc[0:10]