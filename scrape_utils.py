import requests
import pandas as pd
from bs4 import BeautifulSoup

DIV_NAMES = [' MIXED ', ' MENS ', 'CO-ED ', ' OPEN ', ' WOMENS ']

# TODO: do this for college


def parse_club_div(divisions):
    # todo: do this better
    new_divs = []
    for div in divisions:
        for name in DIV_NAMES:
            if name in div:
                new_divs.append(name.strip())
    return new_divs


def clean_data(df, div):
    df = df.copy()
    df.dropna(inplace=True)

    df.columns = df.columns.str.replace(' ', '')

    df.Standing = df.Standing.str.replace('T', '')
    df.Standing = df.Standing.str.replace(' ', '')
    df = df[~df.Standing.isin(['?', 'DQ', 'DNF'])]
    df['Standing'] = df['Standing'].astype(int)

    df = df.rename(columns={'School': 'Team'})

    if div == 'club':
        df.Team = df.Team.str.upper()
    df.Team = df.Team.str.replace('\xa0', '')
    df.Team = df.Team.str.strip()
    df.loc[df.Team == 'Carleton College-Syzygy', 'Team'] = 'Carleton College'
    df.loc[df.Team == 'Massachussets', 'Team'] = 'Massachusetts'

    df.loc[df.division == 'OPEN', 'division'] = 'MENS'
    df.loc[df.division == 'CO-ED', 'division'] = 'MIXED'
    df.loc[df.division == 'DI_O', 'division'] = 'DI_M'
    df.loc[df.division == 'DIII_O', 'division'] = 'DIII_M'

    df.Region = df.Region.str.replace('\xa0', '')
    df.loc[df.Region == 'Sothwest', 'Region'] = 'Southwest'
    df.loc[df.Region == 'Norwest', 'Region'] = 'Northwest'
    df.loc[df.Region == 'Mid-Atlantic', 'Region'] = 'Mid Atlantic'
    df.loc[df.Region == 'SoutentralCh', 'Region'] = 'South Central'
    df.loc[df.Region == 'New England ', 'Region'] = 'New England'
    df.loc[df.Region == 'Oberlin', 'Region'] = 'Ohio Valley'
    df.loc[pd.isna(df.Region), 'Region'] = 'Unknown'
    df.loc[df.Region == '', 'Region'] = 'Unknown'

    if 'SpiritScores' in df.columns:
        df['SpiritScores'] = df['SpiritScores'].str.replace(' *', '')
        df['SpiritScores'] = df['SpiritScores'].str.replace('*', '')
        df['SpiritScores'] = df['SpiritScores'].str.replace(',', '.')
        df['SpiritScores'] = df['SpiritScores'].astype(float)

    df.reset_index(drop=True, inplace=True)
    return df


def get_data_for_year(year, div='club'):
    url = f'https://www.usaultimate.org/archives/{year}_{div}.aspx'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    divisions = []
    for d in soup.find_all('h3'):
        if d.a:
            # for a in d.find_all('a'):
            a = d.find('a')
            div_name = a.attrs.get('name', None)
            # print(div_name)
            if div_name and div_name.startswith('nats_'):
                divisions.append(d.span.text.upper().replace("'", ""))
            elif div_name and div_name.startswith('D') and (div_name.find('_') != -1):
                divisions.append(div_name)


    print(divisions)
    if div == 'club':
        divisions = parse_club_div(divisions)
    print(divisions)

    tables = soup.find_all('table', {'class': 'tablesorter'})
    # assumes nationals tables are first
    tables = tables[0:len(divisions)]
    year_df = pd.DataFrame()
    for i, table in enumerate(tables):
        headings = []
        for h in table.find_all('th'):
            headings.append(h.text.replace("*", ""))
        table_entries = []
        for tr in table.find_all('tr'):
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            table_entries.append(row)
        df_table = pd.DataFrame(table_entries, columns=headings)
        df_table['division'] = divisions[i]
        year_df = pd.concat([year_df, df_table], sort=False)

    if year_df.empty:
        return pd.DataFrame()
    year_df = clean_data(year_df, div)
    year_df['year'] = year
    return year_df
