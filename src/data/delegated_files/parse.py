"""
This script ???

To be filled
"""
import config
import os
import glob
import numpy as np
from datetime import date, datetime, timedelta
import time


def get_date_from_snapshot(file_name):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    # %s/afrinic/delegated-afrinic-extended_%s_%.2d_%.2d.txt
    # Removes paths, then extension trail
    YYYY, mm, dd = file_name.split('/')[-1].split('_')
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


def get_file_name(rir, YYYY, mm, dd):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    if rir == 'ripe':
        file_name = config.path_to_data_storage + '/' + rir + '/' +\
            config.delegation_file_name_structure % (rir + 'ncc', YYYY, mm, dd) + '.bz2'
    elif rir == 'apnic':
        file_name = config.path_to_data_storage + '/' + rir + '/' +\
            config.delegation_file_name_structure % (rir, YYYY, mm, dd) + '.gz'
    else:
        file_name = config.path_to_data_storage + '/' + rir + '/' +\
            config.delegation_file_name_structure % (rir, YYYY, mm, dd)
    return file_name


def unzip_file(rir, file_name):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    if rir == 'ripe':
        os.system('bzip2 -d -f %s' % file_name)
        file_name = file_name[:-4]
    elif rir == 'apnic':
        os.system('gunzip -f %s' % file_name)
        file_name = file_name[:-3]
    return file_name


def create_tmp_file(rir):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    if rir == 'ripe':
        file_name = config.path_to_tmp + '/' + 'tmp.txt.bz2'
    elif rir == 'apnic':
        file_name = config.path_to_tmp + '/' + 'tmp.txt.gz'
    else:
        file_name = config.path_to_tmp + '/' + 'tmp.txt'
    return file_name


def parse_delegation_files(date_init, date_end, rir, output_dir):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    # Creates array of dates
    dates_a = np.array(daterange(date_init, date_end))
    for dt in dates_a:
        YYYY, mm, dd = dt.split('-')
        YYYY = int(YYYY)
        mm = int(mm)
        dd = int(dd)
        # Only parses first monthly snapshot
        if dd == 1:
            # Create a generic tmp file name
            tmp_file_name = create_tmp_file(rir)
            # File name
            file_name = get_file_name(rir, YYYY, mm, dd)
            # Checks if file to be parsed exists
            if len(glob.glob(file_name)) > 0:
                os.system('cp %s %s' % (file_name, tmp_file_name))
                # waits for a while after copying
                time.sleep(2)
                # unzips pch bgp table dump
                # rewrite tmp file name after removing gz extension
                tmp_file_name = unzip_file(rir, tmp_file_name)
                # waits for a while after uziping
                time.sleep(2)
                # filter prefixes v4 from file
                os.system(
                    config.cmd_filter_prefixes_v4 % (
                        tmp_file_name,
                        output_dir + '/prefixes_v4/' + '%s_%.2d_%.2d' % (YYYY, mm, dd)
                    )
                )
                # filter prefixes v6 from file
                os.system(
                    config.cmd_filter_prefixes_v6 % (
                        tmp_file_name,
                        output_dir + '/prefixes_v6/' + '%s_%.2d_%.2d' % (YYYY, mm, dd)
                    )
                )
                # filter ases from file
                os.system(
                    config.cmd_filter_ases % (
                        tmp_file_name,
                        output_dir + '/asns/' + '%s_%.2d_%.2d' % (YYYY, mm, dd)
                    )
                )
                # removes tmp file
                os.system('rm %s' % (tmp_file_name))
                # waits for a while after deleting tmp file 
                time.sleep(2)


def main():
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    date_today = date.today()
    # Iterates for each monitor
    for rir in config.rir_list:
        # Creates output dir
        output_dir = '%s/%s' % (config.path_to_process_data_storage,
                                rir)
        os.system('mkdir -p %s' % output_dir)
        os.system('mkdir -p %s/prefixes_v4' % output_dir)
        os.system('mkdir -p %s/prefixes_v6' % output_dir)
        os.system('mkdir -p %s/asns' % output_dir)
        # Checks if dir to storage data exists.
        #   if exists   --> incremental download
        #   else        --> create dir + download all dataset
        if len(glob.glob(output_dir + '/asns/*')) > 0:
            already_parsed_files = glob.glob(output_dir + '/asns/*')
            # Sorts downloaded files. Latest is going to be the last in the list
            already_parsed_files.sort()
            latest_file_date = get_date_from_snapshot(
                already_parsed_files[-1]
            )
            parse_delegation_files(latest_file_date, date_today,
                                   rir, output_dir)
        # Dir is empty
        else:
            YYYY_i, mm_i, dd_i = config.init_date.split('-')
            # cast number in case it were necessary
            YYYY_i = int(YYYY_i)
            mm_i = int(mm_i)
            dd_i = int(dd_i)
            # Transforms data format of monitor inaguration
            starting_date = date(YYYY_i, mm_i, dd_i)
            parse_delegation_files(starting_date, date_today,
                                   rir, output_dir)


if __name__ == "__main__":
    # execute only if run as a script
    main()
