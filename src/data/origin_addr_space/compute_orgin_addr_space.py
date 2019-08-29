"""
This.

Bla bla.
"""
import pandas as pd
import numpy as np
import config
import radix
from aggregate6 import aggregate
import os
import glob


def load_data(pfix2as_file, pfix_delegation_file):
    """
    This.

    Bla bla.
    """
    # Opens file that contains prefixes and their origin ASes
    pfix2as_df = pd.read_csv(
        pfix2as_file,
        sep='\t',
        names=['network', 'mask', 'origin-asn'],
        compression='gzip'
    )
    # Change data format: two columns (net,mask) --> one column (prefix)
    pfix2as_df['pfix'] = pfix2as_df[['network', 'mask']].apply(
        pfix2as_reformat, axis=1)
    # Drops unnecessary columns
    pfix2as_df = pfix2as_df.drop(['network', 'mask'], axis=1)
    # Opens delegation file
    delegation_file_df = pd.read_csv(
        pfix_delegation_file,
        names=[
            'rir',
            'cc',
            'resource',
            'prefix',
            'address_space-cnt',
            'allocation_date',
            'status',
            'hash'
        ],
        sep='|'
    )
    # Change data format: two columns (net,block_size) --> one column (prefix)
    delegation_file_df['pfix'] = delegation_file_df[
        [
            'prefix',
            'address_space-cnt'
        ]
    ].apply(delegated_reformat, axis=1)
    # Drops unnecessary columns
    delegation_file_df = delegation_file_df[['cc', 'pfix']]
    # Drops misleading records
    delegation_file_df = delegation_file_df.loc[
        delegation_file_df['pfix'] != -1
    ]
    return pfix2as_df, delegation_file_df


class PrefixTree:
    def __init__(self, df):
        """
        This.

        Bla bla.
        """
        # Load tree
        self.rtree = radix.Radix()
        for index, row in df.iterrows():
            prefix = row['pfix']
            cc = row['cc']
            # Look if there is a float in mask
            mask = int(prefix.split('/')[-1])
            if mask <= 24:
                # Crear un nodo al arbol, si no existe se lo agrega
                node = self.rtree.search_exact(prefix)
                rnode = self.rtree.add(prefix)
                rnode.data['cc'] = cc
    def look(self, df):
        """
        This.

        Bla bla.
        """
        # Check if routed prefix in LACNIC
        output_list = []
        for index, row in df.iterrows():
            # subtree = rtree.search_covered(row['pfix'])
            shortest = self.rtree.search_worst(row['pfix'])
            if shortest is not None:
                subtree = self.rtree.search_covered(shortest.prefix)
                sub_prefixes_list = get_prefixes(subtree)
                # There have been a match with LACNIC delegation file
                if len(sub_prefixes_list) > 0:
                    rnode = self.rtree.search_exact(sub_prefixes_list[0])
                    output_list.append(
                        (
                            len(sub_prefixes_list),
                            row['pfix'],
                            row['origin-asn'],
                            rnode.data['cc']
                        )
                    )
        origin_ases_delegation_cc_df = pd.DataFrame(
            output_list,
            columns=[
                'cnt',
                'pfix',
                'origin-asn',
                'cc'
            ]
        )
        return origin_ases_delegation_cc_df


def country_delegation_statistics(origin_ases_delegation_cc_df):
    """
    This.

    Bla bla.
    """
    output_list = []
    for origin_asn, cc in origin_ases_delegation_cc_df.drop_duplicates(
            ['origin-asn', 'cc'])[['origin-asn', 'cc']].values:
        prefix_list = origin_ases_delegation_cc_df.loc[
            (origin_ases_delegation_cc_df['origin-asn'] == origin_asn) &
            (origin_ases_delegation_cc_df['cc'] == cc)
        ]['pfix'].values.tolist()
        aggregated_prefix_list = aggregate(prefix_list)
        ip_cnt = 0
        for prefix in aggregated_prefix_list:
            ip_cnt += prefix_addr_space(prefix)
        output_list.append((cc, origin_asn, ip_cnt))
    # Generate ourput file
    delegated_addr_space_by_as_cc_df = pd.DataFrame(
        output_list,
        columns=[
            'cc',
            'origin-asn',
            'ip-cnt'
        ]
    )
    return delegated_addr_space_by_as_cc_df


def prefix_addr_space(prefix):
    """
    This.

    Bla bla.
    """
    mask = prefix.split('/')[-1]
    return 2 ** (32 - int(mask))


def pfix2as_reformat(row):
    """
    This.

    Bla bla.
    """
    return str(row['network']) + '/' + str(row['mask'])


def delegated_reformat(row):
    """
    This.

    Bla bla.
    """
    network_size = np.log10(row['address_space-cnt']) / np.log10(2)
    if np.floor(network_size) == network_size:
        return str(row['prefix']) + '/'\
            + str(32 - int(network_size))
    else:
        return -1


def get_prefixes(subtree):
    """
    This.

    Bla bla.
    """
    list_pfx = []
    for i in range(len(subtree)):
        list_pfx.append(subtree[i].prefix)
    return list_pfx


def get_dates_from_files(file_name_list):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    output_list = []
    for file_name in file_name_list:
        # Example lg.%s.ptt.br_ipv4_bgp_routes_%s_%.2d_%.2d.txt.gz
        # Removing steps
        # 1) Remove leading path
        # 2) split by `.` and get where the date is (-3 position)
        # 3) split date part by `_` and take last elements where date is
        YYYY, mm, dd = file_name.split('/')[-1].split('_')
        output_list.append((YYYY, mm, dd))
    return output_list


def list_tuple2list_str(input_list):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    output_list = []
    for elem in input_list:
        output_list.append('_'.join(str(e) for e in elem))
    return output_list


def get_dates_not_yet_parsed_files(dates_raw_files, dates_processed_files):
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    # Turns list of tuples into list of strings
    dates_raw_files_str = np.array(list_tuple2list_str(dates_raw_files))
    dates_processed_files_str = np.array(list_tuple2list_str(
        dates_processed_files))
    # get diff set
    diff_array = np.setdiff1d(dates_raw_files_str, dates_processed_files_str)
    # Turns back to list of tuples
    output_list = []
    for date_str in diff_array:
        YYYY, mm, dd = date_str.split('_')
        output_list.append((YYYY, mm, dd))
    return output_list


def compute_origin_addr_space(dates_raw_files, rir, output_dir):
    """
    This.

    Bla bla.
    """
    for YYYY, mm, dd in dates_raw_files:
        # casting
        YYYY = int(YYYY)
        mm = int(mm)
        dd = int(dd)
        print((rir, YYYY, mm, dd))
        # Load data
        # set pfix2as file name
        pfix2as_file = config.path_to_pfix2as_files + '/' +\
            config.pfix2as_file_format % (YYYY, mm, dd)
        # set delegated pfix file name
        pfix_delegation_file = config.path_to_delegated_pfix_files % rir +\
            '/' + '%s_%.2d_%.2d' % (YYYY, mm, dd)
        try:
            pfix2as_df, delegation_file_df = load_data(pfix2as_file,
                                                       pfix_delegation_file)
            flag_available_data = True
        except:
            print('There is no data available')
            flag_available_data = False
        ##########################
        if flag_available_data:
            # Radix: Figure out routed prefixes which were delegated by RIR
            pf = PrefixTree(delegation_file_df)
            origin_ases_delegation_cc_df = pf.look(pfix2as_df)
            # Compute address space originated by country and AS
            delegated_addr_space_by_as_cc_df = country_delegation_statistics(
                origin_ases_delegation_cc_df)
            # Save data
            delegated_addr_space_by_as_cc_df = delegated_addr_space_by_as_cc_df.sort_values(
                ['cc', 'ip-cnt'], ascending=False)
            delegated_addr_space_by_as_cc_df.loc[
                ~delegated_addr_space_by_as_cc_df['cc'].isnull()
            ].to_csv(
                output_dir + '/' + '%s_%.2d_%.2d' % (YYYY, mm, dd),
                header=True,
                index=False
            )


def main():
    """
    Thi is an example script.

    It seems that it has to have THIS docstring with a summary line, a blank line
    and sume more text like here. Wow.
    """
    for rir in ('lacnic', 'ripe', 'apnic', 'afrinic'):
        # Creates output dir
        output_dir = '%s/%s' % (config.path_to_process_data_storage,
                                rir)
        os.system('mkdir -p %s' % output_dir)
        # Gets raw files list
        raw_files_list = glob.glob(config.path_to_delegated_pfix_files % rir + '/*')
        # Checks if dir to storage data exists.
        #   if exists   --> incremental download
        #   else        --> create dir + download all dataset
        if len(glob.glob(output_dir + '/*')) > 0:
            already_computed_files = glob.glob(output_dir + '/*')
            # Get dates from downloaded files
            dates_raw_files = get_dates_from_files(raw_files_list)
            # Get dates from already parsed files
            dates_already_computed_files = get_dates_from_files(
                already_computed_files)
            dates_list = get_dates_not_yet_parsed_files(
                dates_raw_files,
                dates_already_computed_files
            )
            dates_list = np.sort(dates_list)
            # Create a list with dates only from not yet parsed file
            compute_origin_addr_space(dates_list,
                                      rir, output_dir)
        # Dir is empty
        else:
            # Get dates from downloaded files
            dates_raw_files = get_dates_from_files(raw_files_list)
            raw_files_list = np.sort(raw_files_list)
            compute_origin_addr_space(dates_raw_files,
                                      rir, output_dir)


if __name__ == "__main__":
    # execute only if run as a script
    main()
