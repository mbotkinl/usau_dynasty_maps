import pandas as pd
from scrape_utils import get_data_for_year

# start_year = 1979
# end_year = 2018
start_year = 2001
end_year = 2002

all_data = pd.DataFrame()
for year in range(start_year, end_year+1):
    data = get_data_for_year(year)
    all_data = pd.concat([all_data, data], sort=False)


# soup.find_all('h4')
# mydivs = soup.findAll("div", {"class": "top_area winner"})