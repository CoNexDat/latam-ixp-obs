"""
Thi is an example script.

It seems that it has to have THIS docstring with a summary line, a blank line
and sume more text like here. Wow.
"""
import config
import os
import glob
import numpy as np
import time
import pandas as pd
from datetime import timedelta, date, datetime


def get_monitor_placement_date(row):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    YYYY, mm, dd = row['collector_placement_date'].split('-')
    return int(YYYY), int(mm), int(dd)


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


def get_date_from_snapshot(file_name):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    file_name_split = file_name.split('/')[-1].split('_')
    YYYY = int(file_name_split[-3])
    mm = int(file_name_split[-2])
    dd = int(file_name_split[-1])
    return datetime.strptime('%s-%.2d-%.2d' % (YYYY, mm, dd), '%Y-%m-%d').date()


def remove_prepend(path_a):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    _, idx = np.unique(path_a, return_index=True)
    return path_a[np.sort(idx)]


def remove_private_asn(path_a):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    private_range = range(64495, 65535 + 1)
    return path_a[~np.in1d(path_a, private_range)]


def add_mask(raw_pfix):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    if '/' not in raw_pfix:
        first_byte = int(raw_pfix.split('.')[0])
        # DFGW
        if first_byte == 0:
            pfix = raw_pfix + '/0'
        # Class A
        elif first_byte < 128:
            pfix = raw_pfix + '/8'
        # Class B
        elif (first_byte >= 128) and (first_byte < 192):
            pfix = raw_pfix + '/16'
        # Class C
        else:
            pfix = raw_pfix + '/24'
    # prefix already had a mask
    else:
        pfix = raw_pfix
    return pfix


def remove_status_code(pfix):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    # Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
    # r RIB-failure, S Stale, R Removed
    """
    status_code_list = ('s', 'd', 'h', '*', '>', 'i', 'r', 'S', 'R')
    for status_code in status_code_list:
        pfix = pfix.replace(status_code, '')
    return pfix


def get_prefix_path_list_from_table(table):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    output_table_v = []
    flag = True
    next_line_flag = False
    # First 5 lines are header while last 2 are summeary
    for line in table.splitlines()[5:-2]:
        if flag:
            flag = False
            path_i = line.find('Path')
        elif next_line_flag:
                next_line_flag = False
                path = line[path_i:]
                output_table_v.append((pfix, path[:-2]))
        else:
            raw_pfix = line[:20].replace(' ', '')
            # Checks if prefix in line
            if len(raw_pfix) > 2:
                # Removes other irrelevant characters from raw_prefix
                raw_pfix = remove_status_code(raw_pfix)
                # Checks if mask present in prefix
                if '/' in raw_pfix:
                    pfix = raw_pfix
                # No mask. Needs to be added
                else:
                    pfix = add_mask(raw_pfix)
                path = line[path_i:]
                output_table_v.append((pfix, path[:-2]))
            # Sometimes ENTRIES are broken into 2 LINES
            else:
                next_line_flag = True
            output_table_v.append((pfix, path[:-2]))
    return output_table_v


def sanitize_prefix_path_list(prefix_path_list):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    output_file_list = []
    for prefix, path in prefix_path_list:
        raw_path = path.split(' ')
        # checks if there are ASes in the PATH
        if len(path) > 0:
            # Paths might contains AS_SETS {AS1,AS2}.
            # I filter them out
            # Therefore, a TRY is indeed necessary
            try:
                path_a = np.array(np.array(raw_path).astype(int))
                flag = 1
            except:
                flag = 0
            if flag:
                # unpoisoning AS-PATH
                path_a = remove_prepend(path_a)
                path_a = remove_private_asn(path_a)
                output_file_list.append(
                    (prefix, ','.join(str(e) for e in path_a))
                    # (prefix, path_a.tolist()[:].join',')
                )
    return output_file_list


def text2df_table_dump(file_name):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    f = open(file_name, 'r')
    table_dump_str = ''
    table_dump_str = f.read()
    prefix_path_list = get_prefix_path_list_from_table(table_dump_str)
    # Extracting useful information
    clean_prefix_path_list = sanitize_prefix_path_list(prefix_path_list)
    prefix_path_df = pd.DataFrame(
        list(clean_prefix_path_list),
        columns=['prefix', 'as-path'])
    # Drop duplicated lines
    prefix_path_df = prefix_path_df.drop_duplicates(['prefix', 'as-path'])
    return prefix_path_df


def parse_pch_table_dumps(date_init, date_end, iata_code, output_dir):
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
            tmp_file_name = config.path_to_tmp + '/' + 'tmp.txt.gz'
            # File name
            file_name = config.path_to_data_storage % (iata_code) + '/' +\
                config.snapshot_name % (iata_code, YYYY, mm, dd)
            # Checks if file to be parsed exists
            if len(glob.glob(file_name)) > 0:
                os.system('cp %s %s' % (file_name, tmp_file_name))
                # waits for a while after copying
                time.sleep(2)
                # unzips pch bgp table dump
                os.system('gunzip -f %s' % tmp_file_name)
                # waits for a while after uziping
                time.sleep(2)
                # rewrite tmp file name after removing gz extension
                tmp_file_name = tmp_file_name[:-3]
                # Checks if tmp file to be parsed exists
                if len(glob.glob(tmp_file_name)) > 0:
                    prefix_path_df = text2df_table_dump(tmp_file_name)
                    prefix_path_df.to_csv(
                        output_dir + '/' + '%s_%.2d_%.2d' % (YYYY, mm, dd),
                        header=True,
                        index=False
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
    # Open list of monitors of which RIB are going to be downloaded
    pch_monitors_location_df = pd.read_csv(
        config.pch_monitors_location,
        header='infer'
    )
    # Iterates for each monitor
    for index, row in pch_monitors_location_df.iterrows():
        # gets monitor IATA code
        iata_code = row['iata_code']
        # Creates output dir
        output_dir = '%s/%s' % (config.path_to_process_data_storage,
                                iata_code)
        os.system('mkdir -p %s' % output_dir)
        # Checks if dir to storage data exists.
        #   if exists   --> incremental download
        #   else        --> create dir + download all dataset
        if len(glob.glob(output_dir + '/*')) > 0:
            already_parsed_files = glob.glob(output_dir + '/*')
            # Sorts downloaded files. Latest is going to be the last in the list
            already_parsed_files.sort()
            latest_file_date = get_date_from_snapshot(
                already_parsed_files[-1]
            )
            parse_pch_table_dumps(latest_file_date, date_today,
                                  iata_code, output_dir)
        # Dir is empty
        else:
            YYYY_i, mm_i, dd_i = get_monitor_placement_date(row)
            # Transforms data format of monitor inaguration
            starting_date = date(YYYY_i, mm_i, dd_i)
            parse_pch_table_dumps(starting_date, date_today,
                                  iata_code, output_dir)


if __name__ == "__main__":
    # execute only if run as a script
    main()
