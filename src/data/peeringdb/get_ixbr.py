"""
This script.

Author: Esteban Carisimo
Affiliaton: Universidad de Buenos Aires & CONICET
Year: 2019
Description:
    Small piece of code to find out which Netflix's OCAs are candadites for the
    the end-host that is running the code.
    The search of the OCAs is based on the information provided by fast.com
"""

import requests
import config
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os


def extract_iata_code(html_row_list):
    """
    Thi script.

    Author: Esteban Carisimo
    Affiliaton: Universidad de Buenos Aires & CONICET
    Year: 2019
    Description:
        Small piece of code to find out which Netflix's OCAs are candadites for the
        the end-host that is running the code.
        The search of the OCAs is based on the information provided by fast.com
    """
    iata_code = ''
    for row in html_row_list:
        if "Traffic Stats Website" in row.text:
            field = row.text
            traffic_website_url = field.strip().split('\n')[-1]
            iata_code = traffic_website_url.split('/')[-1]
    return iata_code


def main():
    """
    Thi script.

    Author: Esteban Carisimo
    Affiliaton: Universidad de Buenos Aires & CONICET
    Year: 2019
    Description:
        Small piece of code to find out which Netflix's OCAs are candadites for the
        the end-host that is running the code.
        The search of the OCAs is based on the information provided by fast.com
    """
    todays_date = datetime.datetime.now()
    ixp_name = 'ix.br'
    # creates output dir
    os.system('mkdir -p %s%s' % (config.path_to_data, 'ixbr'))
    # HTTP GET
    response = requests.get(config.peeringdb_search_url % ixp_name)
    # Change data structure
    soup = BeautifulSoup(response.text)
    # Look for column where PeeringDB displays `exchanges`
    html_peeringdb_columns_list = soup.find_all(
        'div', {'class': 'col-md-4 col-sm-12 col-xs-12'})
    # Networks is the column in the middle (html_peeringdb_columns_list[0])
    #
    html_ixbr_ixp_list = html_peeringdb_columns_list[0].find_all(
        'div', {'class': 'result_row'})
    # Interest all over the cols
    output_list = []
    for line in html_ixbr_ixp_list:
        # Extract IXP name from line
        ixp_name = line.text
        city_name = ixp_name.split(') ')[-1].strip()
        # Extract URL to IXP entry on PeeringDB
        url_to_ixp_entry = config.peeringdb_url + line.find('a')['href']
        # HTTP GET
        response = requests.get(url_to_ixp_entry)
        # Change data structure
        soup = BeautifulSoup(response.text)
        html_peeringdb_columns_list = soup.find_all(
            'div', {'class': 'row view_row'})
        iata_code = extract_iata_code(html_peeringdb_columns_list)
        output_list.append((iata_code, city_name))
        # print((iata_code, city_name))
    # Turn list into Data Frame
    df = pd.DataFrame(list(output_list),
                      columns=['iata_code', 'city_name'])
    df.to_csv(
        config.ixbr_output_dir % (
            todays_date.year,
            todays_date.month,
            todays_date.day
        ),
        header=True,
        index=False
    )

if __name__ == "__main__":
    # execute only if run as a script
    main()
