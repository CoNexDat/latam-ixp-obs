"""
Thi is an example script.

It seems that it has to have THIS docstring with a summary line, a blank line
and sume more text like here. Wow.
"""
import config
import os
import glob
import time
import pandas as pd
import numpy as np
from datetime import timedelta, date, datetime


def get_monitor_placement_date(row):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    YYYY, mm, dd = row['collector_placement_date'].split('-')
    return int(YYYY), int(mm), int(dd)


def get_date_from_snapshot(file_name):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    file_name_split = file_name.split('.')
    YYYY = int(file_name_split[-4])
    mm = int(file_name_split[-3])
    dd = int(file_name_split[-2])
    return datetime.strptime('%s-%.2d-%.2d' % (YYYY, mm, dd), '%Y-%m-%d').date()


def monitor_rib_download(date_init, date_end, iata_code, target_dir,
                         monthly_granularity=True):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    # Generate list of dates
    dates_a = np.array(daterange(date_init, date_end))
    for dt in dates_a:
        YYYY, mm, dd = dt.split('-')
        # cast number in case it were necessary
        YYYY = int(YYYY)
        mm = int(mm)
        dd = int(dd)
        # Create attributes to download data
        url = config.url_to_data_archive % (YYYY, mm, iata_code) +\
            config.snapshot_name % (iata_code, YYYY, mm, dd)
        output_file = target_dir + '/' +\
            config.snapshot_name % (iata_code, YYYY, mm, dd)
        # monthly_granularity flag is enable, then only download when dd == 1
        if monthly_granularity:
            if dd == 1:
                download(url, output_file)
        else:
            download(url, output_file)
    return None


def download(url, output_file):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    os.system('wget %s -O %s' % (url, output_file))
    time.sleep(10)
    return None


def daterange(date1, date2):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    output_list = []
    for n in range(int((date2 - date1).days) + 1):
        output_list.append((date1 + timedelta(n)).strftime("%Y-%m-%d"))
    return output_list


def main():
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    # sets today datetime variable
    date_today = date.today()
    # Open list of monitors of which RIB are going to be downloaded
    pch_monitors_location_df = pd.read_csv(
        config.pch_monitors_location,
        header='infer'
    )
    # Iterates for each monitor
    for index, row in pch_monitors_location_df.iterrows():
        iata_code = row['iata_code']
        # Gets when the monitor was placed at the IXP
        YYYY_i, mm_i, dd_i = get_monitor_placement_date(row)
        # Transforms data format of monitor inaguration
        starting_date = date(YYYY_i, mm_i, dd_i)
        # Defines path where data is going to be stored
        output_dir = config.path_to_data_storage % iata_code
        # Creates output dir
        os.system('mkdir -p %s' % output_dir)
        # Checks if dir to storage data exists.
        #   if exists   --> incremental download
        #   else        --> create dir + download all dataset
        if len(glob.glob(output_dir)) > 0:
            already_downloaded_files = glob.glob(output_dir + '/*')
            # Sorts downloaded files. Latest is going to be the last in the list
            already_downloaded_files.sort()
            # Checks if output dir is not empty
            if len(already_downloaded_files) > 0:
                # Dir is created but empty. Calls for full download
                latest_file_date = get_date_from_snapshot(
                    already_downloaded_files[-1])
                monitor_rib_download(latest_file_date, date_today,
                                     iata_code, output_dir)
            else:
                # No files
                monitor_rib_download(starting_date, date_today,
                                     iata_code, output_dir)
        # No dir. Calls for full download
        else:
            monitor_rib_download(starting_date, date_today,
                                 iata_code, output_dir)


if __name__ == "__main__":
    # execute only if run as a script
    main()
