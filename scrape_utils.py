import requests
import pandas as pd
from bs4 import BeautifulSoup

# used for renaming divisions
CLUB_DIV_NAMES = [' MIXED ', ' MENS ', 'CO-ED ', ' OPEN ', ' WOMENS ']
COLLEGE_DIV_NAMES = [['D-I ', 'Open'], ['D-I ', 'Men\'s'], ['D-I ', 'Women\'s'], ['D-III ', 'Open'],
                     ['D-III ', 'Men\'s'], ['D-III ', 'Women\'s']]
COLLEGE_DIV_NAMES_2 = ['College Championships: Open Division',
                       'College Championships: Women\'s Division']

# todo: double check all for spelling/duplicate teams (use fuzzy matching) after region/division rework


def parse_college_div(divisions: list) -> list:
    new_divs = []
    for div in divisions:
        for name in COLLEGE_DIV_NAMES:
            if all([n in div for n in name]):
                new_divs.append(''.join(name))
    if not new_divs:
        for div in divisions:
            for name in COLLEGE_DIV_NAMES_2:
                if name in div:
                    new_divs.append(name.strip())
    return new_divs


def parse_club_div(divisions: list) -> list:
    new_divs = []
    for div in divisions:
        for name in CLUB_DIV_NAMES:
            if name in div:
                new_divs.append(name.strip())
    return new_divs


def clean_data(df: pd.DataFrame, div: str, year: int) -> pd.DataFrame:
    df = df.copy()
    df = df.rename(columns={'School': 'Team'})
    df.dropna(subset=['Standing', 'Team'], how='any', inplace=True)

    df.columns = df.columns.str.replace(' ', '')

    df.Standing = df.Standing.str.replace('T', '')  # ties
    df.Standing = df.Standing.str.replace(' ', '')
    df = df[~df.Standing.isin(['?', 'DQ', 'DNF'])]  # remove DQ'd teams
    df['Standing'] = df['Standing'].astype(int)

    if div == 'club':
        df.Team = df.Team.str.upper()
    df.Team = df.Team.str.replace('\xa0', '')
    df.Team = df.Team.str.replace(r'*', '')
    df.Team = df.Team.str.strip()

    # team name corrections
    # college
    df.loc[df.Team == 'Carleton College-Syzygy', 'Team'] = 'Carleton College'
    df.loc[df.Team == 'Massachussets', 'Team'] = 'Massachusetts'
    df.loc[df.Team == 'Northwestern', 'Region'] = 'Great Lakes'

    # club
    df.loc[df.Team == 'BOHDI', 'Team'] = 'BODHI'
    df.loc[df.Team == 'SHAME', 'Team'] = 'SHAME.'
    df.loc[df.Team == 'ODYSSEE', 'Team'] = 'ODYSSÉE.'
    df.loc[df.Team == 'GRAFITTI', 'Team'] = 'GRAFFITI'
    df.loc[df.Team == 'DISCTRICT 5', 'Team'] = 'DISTRICT 5'
    df.loc[df.Team == 'HOLES AND POLES', 'Team'] = 'HOLES & POLES'
    df.loc[df.Team == 'HOMEBROOD', 'Team'] = 'HOME BROOD'
    df.loc[df.Team == '7EXPRESS', 'Team'] = '7 EXPRESS'
    df.loc[df.Team == 'COLUMBUS COCKTAILS', 'Team'] = 'COCKTAILS'
    df.loc[df.Team == 'LOOSE CANON', 'Team'] = 'LOOSE CANNON'

    # division corrections
    df.loc[df.division == 'OPEN', 'division'] = 'MENS'
    df.loc[df.division == 'CO-ED', 'division'] = 'MIXED'
    df.loc[df.division == 'D-I Open', 'division'] = 'D-I Men\'s'
    df.loc[df.division == 'D-III Open', 'division'] = 'D-III Men\'s'
    df.loc[df.division == 'College Championships: Open Division', 'division'] = 'Men\'s'
    df.loc[df.division == 'College Championships: Women\'s Division', 'division'] = 'Women\'s'

    # region corrections
    df.Region = df.Region.str.replace('\xa0', '')
    df.loc[df.Region == 'Sothwest', 'Region'] = 'Southwest'
    df.loc[df.Region == 'Norwest', 'Region'] = 'Northwest'
    df.loc[df.Region == 'Mid-Atlantic', 'Region'] = 'Mid Atlantic'
    df.loc[df.Region == 'SoutentralCh', 'Region'] = 'South Central'
    df.loc[df.Region == 'New England ', 'Region'] = 'New England'
    df.loc[df.Region == 'Oberlin', 'Region'] = 'Ohio Valley'
    df.loc[pd.isna(df.Region), 'Region'] = 'Unknown'
    df.loc[df.Region == '', 'Region'] = 'Unknown'

    if div == 'club':
        df.loc[df.Region == 'Central', 'Region'] = 'Central (pre-2012)'
        df.loc[df.Region == 'South', 'Region'] = 'South (pre-2012)'
        df.loc[df.Region == 'West', 'Region'] = 'West (pre-1995)'
    elif div == 'college':
        df.loc[df.division == 'Men\'s', 'division'] = 'Men\'s (pre-2010)'
        df.loc[df.division == 'Women\'s', 'division'] = 'Women\'s (pre-2010)'
        df.loc[df.Region == 'Central', 'Region'] = 'Central (pre-2011)'
        df.loc[df.Region == 'South', 'Region'] = 'South (pre-2011)'
        df.loc[df.Region == 'Mid Atlantic', 'Region'] = 'Mid Atlantic (pre-1999)'
        df.loc[df.Region == 'Northeast', 'Region'] = 'Northeast (pre-1999)'
        df.loc[df.Region == 'West', 'Region'] = 'West (pre-1999)'

    # spirit scores corrections
    if 'SpiritScores' in df.columns:
        df['SpiritScores'] = df['SpiritScores'].str.replace(' *', '')
        df['SpiritScores'] = df['SpiritScores'].str.replace('*', '')
        df['SpiritScores'] = df['SpiritScores'].str.replace(',', '.')
        df['SpiritScores'] = df['SpiritScores'].astype(float)

        # convert old spirit score (1-5) to WFDF system (0-20)
        if year <= 2013:
            # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
            # OldMin = 1
            # OldMax = 5
            # NewMin = 0
            # NewMax = 20
            df['SpiritScores'] = ((df['SpiritScores'] - 1) * 20) / 4

    df.reset_index(drop=True, inplace=True)
    return df


def get_data_for_year(year: int, div: str) -> pd.DataFrame:

    # get request from usau archives site
    url = f'https://www.usaultimate.org/archives/{year}_{div}.aspx'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    # get divisions from headers
    divisions = []
    for d in soup.find_all('h3'):
        if d.a:
            if div == 'club':
                for a in d.find_all('a'):
                    div_name = a.attrs.get('name', None)
                    if div_name and div_name.startswith('nats_'):
                        divisions.append(d.span.text.upper().replace("'", ""))
            elif div == 'college':
                if d.text and ((d.text.find('-') != -1) | (d.text.find(':') != -1)):
                    divisions.append(d.text)

    # rename divisions
    print(divisions)
    if div == 'club':
        divisions = parse_club_div(divisions)
    elif div == 'college':
        divisions = parse_college_div(divisions)
    print(divisions)

    # placement data are in tables
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

    # clean data
    year_df = clean_data(year_df, div, year)
    year_df['year'] = year

    return year_df


def region_correction(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    if df['Region'].nunique() > 1:
        df = df.copy()
        df = df.sort_values('year', ascending=False)
        df['Region'] = df['Region'].iloc[0]
        return df
    else:
        return df
