"""
This script downloads BGP table dumps and communities from IX.br.

Commands were taken from Brito et al. (University of Campinas - UNICAMP)
This script is publicly available in:
https://github.com/intrig-unicamp/ixp-ptt-br/blob/master/raw_data/IXbr-RAW.sh
"""
import config
import os
import glob
import pandas as pd
from datetime import date, datetime


def main():
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    date_today = date.today().strftime("%Y-%m-%d")
    YYYY, mm, dd = date_today.split('-')
    # sets today datetime variable
    ixbr_location_files = glob.glob(config.path_to_location_files + '/*')
    # Sort files by date
    ixbr_location_files.sort()
    # Download according to the latest dat obtained from PeeringDB
    ixbr_locations_df = pd.read_csv(ixbr_location_files[-1], header='infer')
    for ixp in ixbr_locations_df['iata_code'].values:
        os.system('mkdir -p %s/%s/ribs' % (config.path_to_data, ixp))
        os.system('mkdir -p %s/%s/communities' % (config.path_to_data, ixp))
        os.system(config.download_bgp_v4_aspaths % (
            ixp,
            config.path_to_data + '/' + ixp + '/ribs',
            ixp,
            YYYY,
            int(mm),
            int(dd)
        )
        )
        os.system(config.download_bgp_communities % (
            ixp,
            config.path_to_data + '/' + ixp + '/communities',
            ixp,
            YYYY,
            int(mm),
            int(dd)
        )
        )
if __name__ == "__main__":
    # execute only if run as a script
    main()
