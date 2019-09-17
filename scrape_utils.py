import requests
import pandas as pd
from bs4 import BeautifulSoup


def parse_div(divs):
    # TODO: do this
    return ['Mixed', 'Open', 'Womens']


def clean_data(df):
    df = df.copy()
    df.Standing = df.Standing.str.replace('T', '')
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def get_data_for_year(year):
    # url = 'https://play.usaultimate.org/events/USA-Ultimate-National-Championships-2015/schedule/Men/Club-Men/'
    # url = 'https://www.usaultimate.org/archives/2018_club.aspx'
    # url = 'https://www.usaultimate.org/archives/2001_club.aspx'
    url = f'https://www.usaultimate.org/archives/{year}_club.aspx'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    divisions = []
    for d in soup.find_all('h3'):
        if d.a:
            for a in d.find_all('a'):
                div_name = a.attrs.get('name', None)
                if div_name and div_name.startswith('nats'):
                    divisions.append(d.span.text)

    divisions = parse_div(divisions)

    tables = soup.find_all('table', {'class': 'tablesorter'})

    year_df = pd.DataFrame()
    for i, table in enumerate(tables):
        headings = []
        for h in table.find_all('th'):
            headings.append(h.text)
        table_entries = []
        for tr in table.find_all('tr'):
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            table_entries.append(row)
        df_table = pd.DataFrame(table_entries, columns=headings)
        df_table['division'] = divisions[i]
        year_df = pd.concat([year_df, df_table], sort=False)

    year_df = clean_data(year_df)
    year_df['year'] = year
    return year_df
