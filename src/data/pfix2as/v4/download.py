"""
This script ???

To be filled
"""
import config
import os
import glob
import numpy as np
from datetime import date, datetime, timedelta
import requests
from bs4 import BeautifulSoup


def get_resource_to_download(url):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    file_name = ''
    # Gets pfix2as archive website
    response = requests.get(url)
    # Data transformation
    soup = BeautifulSoup(response.text)
    # Look for href to files
    pfix2as_website_href_list = soup.find_all('a')
    for href in pfix2as_website_href_list:
        # First file that contains 'routeviews-rv2-' is the first monthly snapshot
        if 'routeviews-rv2-' in href.text:
            file_name = href.text
            break
    return file_name


def get_date_from_snapshot(file_name):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    # '../../../../data/raw/pfix2as/routeviews-rv2-20190501.pfx2as.gz'
    # Removes paths, then extension trail and finally file name indicator
    date_date = str(file_name.split('/')[-1].split('.')[0].split('-')[-1])
    YYYY = int(date_date[:4])
    mm = int(date_date[4:6])
    dd = int(date_date[6:8])
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
    os.system('mkdir -p %s' % config.path_to_data_storage)
    if len(glob.glob(config.path_to_data_storage + '/*')) > 0:
        # creates a list with all already downloaded files
        pfix2as_files = glob.glob(config.path_to_data_storage + '/*')
        pfix2as_files.sort()
        init_date_dt = get_date_from_snapshot(pfix2as_files[-1])
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
            pfix2as_file_name = get_resource_to_download(
                config.pfx2as_website_archive % (YYYY, mm)
            )
            if pfix2as_file_name != '':
                # Download AS-REL file
                os.system(
                    config.url_to_file % (
                        YYYY,
                        mm,
                        pfix2as_file_name,
                        config.path_to_data_storage,
                        YYYY,
                        mm,
                        dd
                    )
                )


if __name__ == "__main__":
    # execute only if run as a script
    main()
