"""
This script ???

To be filled
"""
import config
import os
import glob
import numpy as np
from datetime import date, datetime, timedelta


def get_date_from_snapshot(file_name):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    # %s/afrinic/delegated-afrinic-extended_%s_%.2d_%.2d.txt
    # Removes paths, delegation file name structure, then extension trail
    YYYY, mm, dd = file_name.split('/')[-1].split('-')[-1].split('.')[0].split('_')
    YYYY = int(YYYY)
    mm = int(mm)
    dd = int(dd)
    # if month found then go to next month
    if mm == 12:
        YYYY += 1
        mm = 1
    else:
        mm += 1
    # Overwrites day
    dd = 1
    return datetime.strptime('%s-%.2d-%.2d' % (YYYY, mm, dd), '%Y-%m-%d').date()


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
    # creates output dir
    os.system('mkdir -p %s/arin' % config.path_to_data_storage)
    os.system('mkdir -p %s/ripe' % config.path_to_data_storage)
    os.system('mkdir -p %s/apnic' % config.path_to_data_storage)
    os.system('mkdir -p %s/lacnic' % config.path_to_data_storage)
    os.system('mkdir -p %s/afrinic' % config.path_to_data_storage)
    if len(glob.glob(config.path_to_data_storage + '/arin/*')) > 0:
        # creates a list with all already downloaded files
        asrel_files = glob.glob(config.path_to_data_storage + '/arin/*')
        asrel_files.sort()
        init_date_dt = get_date_from_snapshot(asrel_files[-1])
    else:
        # Turns into datetime format date of first snapshot
        init_date_dt = datetime.strptime(config.init_date, '%Y-%m-%d').date()
    # Get today's date
    date_today_dt = date.today()
    dates_a = np.array(daterange(init_date_dt, date_today_dt))
    # Iterates
    for dt in dates_a:
        YYYY, mm, dd = dt.split('-')
        # cast number in case it were necessary
        YYYY = int(YYYY)
        mm = int(mm)
        dd = int(dd)
        # AS-REL files are released dd==01
        if dd == 1:
            # Download delegation files
            # ARIN
            os.system(config.cmd_arin % (
                YYYY,
                mm,
                dd,
                config.path_to_data_storage,
                YYYY,
                mm,
                dd
            )
            )
            # RIPE
            os.system(config.cmd_ripe % (
                YYYY,
                YYYY,
                mm,
                dd,
                config.path_to_data_storage,
                YYYY,
                mm,
                dd
            )
            )
            # APNIC
            os.system(config.cmd_apnic % (
                YYYY,
                YYYY,
                mm,
                dd,
                config.path_to_data_storage,
                YYYY,
                mm,
                dd
            )
            )
            # LACNIC
            os.system(config.cmd_lacnic % (
                YYYY,
                mm,
                dd,
                config.path_to_data_storage,
                YYYY,
                mm,
                dd
            )
            )
            # AFRINIC
            os.system(config.cmd_afrinic % (
                YYYY,
                YYYY,
                mm,
                dd,
                config.path_to_data_storage,
                YYYY,
                mm,
                dd
            )
            )

if __name__ == "__main__":
    # execute only if run as a script
    main()
