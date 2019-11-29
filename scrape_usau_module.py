import pandas as pd
from scrape_utils import get_data_for_year

start_year = 1979
end_year = 2019
# start_year = 2000
# end_year = 2002

all_data = pd.DataFrame()
for year in range(start_year, end_year+1):
    print(year)
    data = get_data_for_year(year)
    all_data = pd.concat([all_data, data], sort=False)

all_data.to_csv('./data/national_data.csv', index=False)
