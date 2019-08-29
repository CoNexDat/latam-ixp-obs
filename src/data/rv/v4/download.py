"""
Script to download RIBs from multiple monitors in RouteViews.

The script relies on the values of the variables defined in config.py. It
downloads RIBs from years Y_I to Y_F (included), on the day DAY and for monitors
MONITORS of RouteViews and stores them in PATH_TO_DATA_STORAGE. The script
prints to stdout: i) the monitor for which the data is being downloaded and ii)
if the data for the considered month was actually found or not. The data is
stored in PATH_TO_DATA_STORAGE, with a folder for each monitor, which in turn
also contains one folder per year. Each of this gathers the RIBs that were
downloaded for that year.
"""
from config import *
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
from dateutil.relativedelta import relativedelta


def ensure_dir(path):
    """
    Creates a path, if it does not exist already.

    Takes a path as argument, and, if it does not already exist, makes the
    necessary directories to create it.
    """
    if not os.path.exists(path):
        # print("Creating Directory: %s" % path)
        os.makedirs(path)
    return None


def is_folder_empty(path):
    """
    Checks if a folder is empty.

    Takes a path as argument, and returns True if it does not include any file.
    Otherwise, returns False.
    """
    for dirpath, dirnames, files in os.walk(path):
        if not files:
            return True
        return False


def exists_url(url):
    """
    Checks weather an URL exists or not.

    Makes an HTTP request towards the URL it receives. If the request returns
    an HTTP error code, the URL is assumed inexistent and the function returns
    False. Otherwise, the function returns True.
    """
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        # print(err)
        return False
    return True


def success_downloading_rib(monitor, url, filename, year):
    """
    Relying on wget, downloads a RIB with a certain filename.

    Tries to download a RIB of a monitor, dumped on a given year. It searches
    in a URL for a specific RIB with a given filename. Returns True if it was
    able to download the RIB, or False otherwise.
    """
    file = url + filename
    output_filename = filename.split(".")[0] + "." + filename.split(".")[1] + \
                      "." + filename.split(".")[3]
    command = 'wget -q %s -O %s/%s' % (file,
                                       PATH_TO_DATA_STORAGE % monitor,
                                       output_filename)
    error_code = os.WEXITSTATUS(os.system(command))
    if not error_code:
        return True
    os.system('rm %s/%s' % (PATH_TO_DATA_STORAGE % monitor, output_filename))
    return False


def exists_rib_dumped_at_usual_hours(monitor, url, year, month):
    """
    Downloads a RIB of a monitor dumped at usual hours.

    Takes a monitor, url, year and month as arguments, and looks for RIBs
    dumped at usual times (hours defined in config.py as HOURS_DUMP). Returns
    True if it finds a RIB, or False otherwise.
    """
    for hour in HOURS_DUMP:
        filename = FILENAME_TO_DOWNLOAD % (year, month, DAY, hour)
        if(success_downloading_rib(monitor, url, filename, year)):
            return True
    return False


def exists_any_rib_dumped(monitor, url, year, month):
    """
    Downloads a RIB of a monitor dumped at any hour.

    Takes a monitor, url, year and month as arguments, and, if a RIB for that
    monitor on that date (DAY defined in config.py) exists, it downloads the
    first one it finds. Returns True if it finds a RIB, or False otherwise.
    """
    html_page = urlopen(url)
    soup = BeautifulSoup(html_page, "html.parser")
    filename = soup.select_one("a[href*='%s%s%s']" % (year, month, DAY))
    if not filename:
        return False
    filename = filename.get("href")
    return success_downloading_rib(monitor, url, filename, year)


def download_current_RIB(monitor, year, month):
    """
    Downloads a RIB of a monitor, on a given date.

    Takes a monitor, year and month as arguments and, if a RIB for that monitor
    on that date (DAY defined in config.py) exists, it downloads the first one
    it finds. The search starts looking for RIBs dumped at the usual times and
    then at no matter what time. Returns True if it finds a RIB, None if there
    is no data that month (the URL does not exist) and False when there is no
    data on that specific date (URL exists, but no files were found).
    """
    url = URL % (monitor, "%s.%s" % (year, month))
    # Check if URL exists
    if not(exists_url(url)):
        # URL does not exist
        return None
    # If URL exists, download a RIB dumped at usual times
    if(exists_rib_dumped_at_usual_hours(monitor, url, year, month)):
        return True
    # If no RIB was found, look for RIBs dumped at any time of the day
    if(exists_any_rib_dumped(monitor, url, year, month)):
        return True
    # URL exists, but no RIB was dumped on that date
    return False


def print_status(is_success):
    """
    Prints to stdout about the succeed of downloading a RIB a given date.

    Takes the monitor for which the RIB was being downloaded, and another
    variable indicating if the script was actually able to get it. It prints
    out data for the user, according to the values of the latter variable
    (True -> OK, None -> Missing URL, False -> Missing File).
    """
    if is_success:
        print("OK")
    elif is_success is None:
        print("URL Not Found: missing data that month?")
    else:
        print("DATA Missing: missing data that day?")


def get_last_date_downloaded(path, monitor):
    try:
        date_str = sorted(os.listdir(path))[-1].split(".")[1]
        return datetime.strptime(date_str, '%Y%m%d')
    except IndexError:
        date_str = MONITORS_YEAR_OF_DEPLOY[monitor] + "01" + DAY
        return datetime.strptime(date_str, '%Y%m%d') - relativedelta(months=1)


def download_yearly_explicit_data_main():
    """
    Downloads one RIB per month, for the defined day, years and monitors.

    Relies on the values of the variables defined in config.py to download RIBs
    from years Y_I to Y_F (included), on the day DAY and for monitors MONITORS.
    The data is stored in PATH_TO_DATA_STORAGE.
    """
    for monitor in MONITORS:
        print("MONITOR: %s" % monitor)
        current_storage_path = PATH_TO_DATA_STORAGE % monitor
        for y in range(Y_I, Y_F + 1):
            year = str(y)
            print("\tYEAR: %s -- Data Path: %s" % (year, current_storage_path))
            for month in ["%.2d" % i for i in range(1, 13)]:
                print("\t%s: " % month, end="")
                print_status(monitor, download_current_RIB(monitor, year, month))


def incremental_download_main():
    """
    Downloads one RIB per month, for the defined day, years and monitors, only
    if they have not been downloaded yet.

    Relies on the values of the variables defined in config.py to download RIBs
    on the day DAY and for monitors MONITORS. The data is stored in
    PATH_TO_DATA_STORAGE.
    """
    for monitor in MONITORS:
        print("MONITOR: %s" % monitor)
        current_storage_path = PATH_TO_DATA_STORAGE % monitor
        ensure_dir(current_storage_path)
        last_date_now = get_last_date_downloaded(current_storage_path, monitor)
        last_date_new = datetime.now().replace(day=int(DAY))
        if last_date_now.date() == last_date_new.date():
            print("\tNo new data to download, exiting")
            continue
        print("\tOld: %s\n\tNew: %s" % (last_date_now.date(),
                                        last_date_new.date()))
        while(True):
            last_date_now += relativedelta(months=1)
            year = last_date_now.year
            month = '%02d' % last_date_now.month
            print("%s:" % last_date_now.date(), end =" ")
            print_status(download_current_RIB(monitor, year, month))
            if last_date_now.date() == last_date_new.date():
                break

if __name__ == "__main__":
    # download_yearly_explit_data_main()
    incremental_download_main()