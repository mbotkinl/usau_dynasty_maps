import pandas as pd
from scrape_utils import get_data_for_year, region_correction

# years to scrap
start_year = 1979
end_year = 2019

# each year get club and college data
all_data = pd.DataFrame()
for year in range(start_year, end_year+1):
    print(year)
    club_data = get_data_for_year(year, div='club')
    club_data['comp_division'] = 'Club'
    col_data = get_data_for_year(year, div='college')
    col_data['comp_division'] = 'College'
    all_data = pd.concat([all_data, club_data, col_data], sort=False)

all_data.year = all_data.year.astype(int)
all_data.Standing = all_data.Standing.astype(int)

# if team exists in later region use that one
all_data_corrected = all_data.groupby(['comp_division', 'division', 'Team']).apply(region_correction).\
    reset_index(drop=True)


# save data
all_data_corrected.to_csv('./data/national_data.csv', index=False)
