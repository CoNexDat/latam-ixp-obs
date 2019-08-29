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


def extract_data_from_entry(entry):
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
    if ' - ' in entry:
        ixp_code, name_and_asn = entry.split(' - ')
        pseudo_iata_code = ixp_code.split('-')[-1]
        asn = int(name_and_asn.split('(')[-1].split(')')[0])
        if name_and_asn.count('(') == 2:
            city_name = name_and_asn.split('(')[1].split(')')[0]
        else:
            city_name = ''
    else:
        ixp_code, name_and_asn = entry.split(' ')
        pseudo_iata_code = ixp_code.split('-')[-1]
        asn = int(name_and_asn.split('(')[-1].split(')')[0])
        city_name = ''
    return pseudo_iata_code, city_name, asn


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
    ixp_name = 'cabase'
    # creates output dir
    os.system('mkdir -p %s%s' % (config.path_to_data, ixp_name))
    # HTTP GET
    response = requests.get(config.peeringdb_search_url % ixp_name)
    # Change data structure
    soup = BeautifulSoup(response.text)
    # Look for column where PeeringDB displays `networks`
    html_peeringdb_columns_list = soup.find_all(
        'div', {'class': 'col-md-4 col-sm-12 col-xs-12'})
    # Networks is the column in the middle (html_peeringdb_columns_list[1])
    #
    html_cabase_ixp_list = html_peeringdb_columns_list[1].find_all(
        'div', {'class': 'result_row'})
    # Interest all over the cols
    output_list = []
    for line in html_cabase_ixp_list:
        # print(extract_data_from_entry(line.text))
        output_list.append((extract_data_from_entry(line.text)))
    # Turn list into Data Frame
    df = pd.DataFrame(list(output_list),
                      columns=['iata_code', 'city_name', 'asn'])
    df.to_csv(
        config.cabase_output_dir % (
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
