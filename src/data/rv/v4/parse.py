"""
Script to parse RIBs downloaded from RouteViews.

The script parses the RIBs previously downloaded using the script download.py,
and outputs a csv file per RIB such that: 1st column is the prefix, 2nd column
is the AS-path. The script uses some variables that are defined in config.py
and a function already defined in download.py.
"""
from config import *
from download import ensure_dir, get_last_date_downloaded
import sys
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def includes_as_set(as_path):
    """
    Check whether an AS-path includes an AS-set.

    Takes as AS-path as a string and looks whether it includes the characters
    "{" or "}", which are usually used to indicate the presence of an AS-set.
    """
    if('{' in as_path or '}' in as_path):
        return True
    return False


def is_documentation_asn(asn):
    """
    Check whether an ASN is an ASN reserved for documentation.

    Takes as ASN as an integer and checks whether it is in the range of values
    reserved for documentation.
    """
    if((asn >= 64496 and asn <= 64511) or \
       (asn >= 65536 and asn <= 65551)):
            return True
    return False


def is_private_asn(asn):
    """
    Check whether an ASN is a private ASN.

    Takes as ASN as an integer and checks whether it is in the range of values
    reserved to be used as private ASNs.
    """
    if((asn >= 64512 and asn <= 65534) or \
       (asn >= 4200000000 and asn <= 4294967294)):
            return True
    return False


def is_reserved_asn(asn):
    """
    Check whether an ASN is a reserved ASN.

    Takes as ASN as an integer and checks whether it is in the range of values
    reserved and not to be used.
    """
    if((asn >= 65552 and asn <= 131071) or \
        asn == 0 or \
        asn == 65535 or \
        asn == 4294967295):
            return True
    return False


def is_unallocated_asn(asn):
    """
    Check wether an ASN is an unallocated ASN.

    Takes as ASN as an integer and checks whether it is in the range of values
    unallocated.
    """
    if((asn >= 139578 and asn <= 196607) or \
       (asn >= 207260 and asn <= 262143) or \
       (asn >= 268701 and asn <= 327679) or \
       (asn >= 328704 and asn <= 393215) or \
       (asn >= 397213 and asn <= 4199999999)):
            return True
    return False


def is_invalid_asn(asn):
    """
    Check whether an ASN is an invalid ASN to advertise in BGP.

    Takes as ASN as an integer and checks whether it is a reserved, reserved
    for documentation, private or unallocated ASN. These values are defined in
    https://www.iana.org/assignments/as-numbers/as-numbers.xhtml and should not
    be advertised in BGP.
    """
    if(is_documentation_asn(asn) or is_private_asn(asn) or \
       is_reserved_asn(asn) or is_unallocated_asn(asn)):
            return True
    return False


def eliminate_invalid_asns(as_path):
    """
    Eliminate invalid ASNs an AS-path might include.

    Takes an AS-path as a list of string-ASNs, and looks if any of the ASNs
    that compose it are invalid ASNs. If they are, they are eliminated from the
    AS-path. The AS-path should not include AS-sets when calling this function.
    """
    j = len(as_path)
    while j:
        asn = int(as_path[j - 1])
        if is_invalid_asn(asn):
            as_path.pop(j - 1)
        j -= 1
    return as_path


def eliminate_as_prepending(as_path):
    """
    Eliminate AS-prepending an AS-path might include.

    Takes an AS-path as a list of string-ASNs and, if ASNs repeat in a row,
    eliminates the repetitions such that each ASN appears once (if the AS-path
    includes no loops).
    """
    j = 0
    while(j < len(as_path) - 1):
        asn = as_path[j]
        while(as_path[j + 1] == asn):
                as_path.pop(j + 1)
                if (j == len(as_path) - 1):
                    break
        j += 1
    return as_path


def extract_BGP_data(list_entry):
    """
    Read the BGP data of interest from an entry in a RIB.

    Takes a entry of a RIB, previously splitted by spaces, as entry and returns
    the prefix, next-hop, feed-AS and AS-path associated to that entry.  
    """
    prefix   = list_entry[PREFIX_FIELD]
    as_path  = list_entry[AS_PATH_FIELD]
    if MRT_DUMP_TOOL == 'bgpdump':
        next_hop = list_entry[NEXT_HOP_FIELD]
        feed_as  = list_entry[FEEDING_AS_FIELD]
    elif MRT_DUMP_TOOL == 'bgpscanner':
        next_hop = list_entry[NH_AND_FEED_AS_FIELD].split(" ")[NEXT_HOP_SUBFIELD]
        feed_as  = list_entry[NH_AND_FEED_AS_FIELD].split(" ")[FEEDING_AS_SUBFIELD]
    return [prefix, next_hop, feed_as, as_path]


def is_correct_ip_version(prefix, next_hop):
    """
    Check whether the prefix and next-hop are associatted to IPv4 or IPv6.

    Takes a prefix and a next-hop and, checks whether they belong to the IP
    version defined in config.py. TODO: IPv6 filtering.
    """
    if IP_VERSION == "v4":
        if(prefix == "0.0.0.0/0" or ":" in prefix or ":" in next_hop):
            return False
    return True


def convert_to_output_format(as_path):
    """
    Convert a list of ASNs into a string.

    Takes an AS-path as a list of string-ASNs, and converts it into a unique
    string where ASNs are separated by commas. The last comma is omitted.
    """
    if(len(as_path) == 1):
        return as_path[0]
    as_path_output_format = ''
    for asn in as_path:
        as_path_output_format += asn + ","
    return as_path_output_format[:-1]


def process_as_path(as_path):
    """
    Process AS-path read from an entry in a RIB.

    Takes an AS-path as a string, and process it eliminating prepending and
    invalid ASNs. Finally, the AS-path is converted to the required output
    format.
    """
    as_path = as_path.strip().split(" ")
    as_path = eliminate_as_prepending(eliminate_invalid_asns(as_path))
    as_path = convert_to_output_format(as_path)
    return as_path


def add_feed_as_data(feed_ases, feed_as, prefix, as_path):
    """
    Update the dictionary of feed-as.

    Takes a dictionary of feed-ASes and adds data concerning to one entry read
    in a RIB related to a given feed-AS.

    """
    if feed_as not in feed_ases:
        feed_ases[feed_as] = []
    feed_ases[feed_as].append([prefix, as_path])
    return feed_ases


def extract_data_per_feeding_as(dumped_rib_file):
    """
    Extract prefixes and their associated AS-paths from a RIB, per feeding AS.

    Takes a RIB dumped with bgpdump, and returns a dictionary in which the key
    words are feed-ASes. Each of them contains a list of the prefixes and
    AS-path that they advertised.
    """
    feed_ases = {}
    with open(dumped_rib_file, "rt") as rib_file:
        for entry in rib_file:
            list_entry = entry.split('|')
            if (len(list_entry) != N_FIELDS_BGP_ENTRY):
                continue
            [prefix, next_hop, feed_as, as_path] = extract_BGP_data(list_entry)
            if((not is_correct_ip_version(prefix, next_hop)) or \
                includes_as_set(as_path)):
                    continue
            as_path = process_as_path(as_path)
            feed_ases = add_feed_as_data(feed_ases, feed_as, prefix, as_path)
    os.remove(dumped_rib_file)
    return feed_ases


def print_route_server_data_to_file(feed_ases, year, month, output_folder):
    """
    Print Route Server data to file.

    If data from the Route Server of Brazil is found on a dictionary of feed
    ASes, storing prefixes associated wit as-paths, the data is print to file
    in the output folder.
    """
    if "26162" not in feed_ases:
        print("\t\tERROR: Route server data missing")
        return
    df_route_server = pd.DataFrame(feed_ases["26162"],
                                   columns=["prefix", "as-path"])
    output_filename = "%s_%s_%s" % (year, month, DAY)
    df_route_server.to_csv(os.path.join(output_folder, output_filename),
                           index=False, encoding='utf-8')


def command_for_mrt_dump_tool(dumped_rib, raw_rib):
    if MRT_DUMP_TOOL == 'bgpdump':
        # return "bgpdump -m -O %s %s" % (dumped_rib, raw_rib)
        return "bgpdump -m %s | grep '%s' > %s" % (raw_rib, "|26162|", dumped_rib)
    elif MRT_DUMP_TOOL == 'bgpscanner':
        return "bgpscanner -a %s -o %s %s" % ("26162", dumped_rib, raw_rib)


def get_last_date_parsed(path, monitor):
    try:
        date_str = sorted(os.listdir(path))[-1]
        return datetime.strptime(date_str, '%Y_%m_%d')
    except IndexError:
        return None

def parse_all_available_files_main():
    """
    Create a file storing the prefixes and AS-paths advertised by th RS in SP.

    Takes the raw-RIBs obtained with download.py and dumps them with bgpdump. 
    Then, the feed-ASes of each year and month are extracted and the data is
    stored in a csv file per RIB read: 1st column prefix, 2nd column AS-path.
    """
    ensure_dir(PATH_TO_TMP)
    for monitor in MONITORS:
        print("MONITOR: %s" % monitor)
        path_to_data_now = PATH_TO_DATA_STORAGE % monitor
        if(not os.path.isdir(path_to_data_now)):
            print("%s: No data available for this monitor " % monitor)
            continue
        output_folder = PATH_TO_PROCESS_DATA_STORAGE % monitor
        ensure_dir(output_folder)
        qfiles = len(os.listdir(path_to_data_now))
        for n, filename in enumerate(sorted(os.listdir(path_to_data_now))):
            print("\t\tTreating: %s  (%s/%s)" % (filename, 1 + n, qfiles))
            year = filename[4:8]
            raw_rib = os.path.join(path_to_data_now, filename)
            dumped_rib = os.path.join(PATH_TO_TMP, filename[:-3] + "txt")
            command = command_for_mrt_dump_tool(dumped_rib, raw_rib)
            os.system(command)    
            feed_ases = extract_data_per_feeding_as(dumped_rib)
            print_route_server_data_to_file(feed_ases, year, 
                                            filename.split(".")[1][4:6],
                                            output_folder)


def incremental_parse_main():
    """
    Incrementally adds stores prefixes and AS-paths advertised by th RS in SP.

    Takes the raw-RIBs obtained with download.py and dumps them with bgpdump. 
    Then, the feed-ASes of each year and month are extracted and the data is
    stored in a csv file per RIB read: 1st column prefix, 2nd column AS-path.
    """
    ensure_dir(PATH_TO_TMP)
    for monitor in MONITORS:
        print("MONITOR: %s" % monitor)
        path_to_data_now = PATH_TO_DATA_STORAGE % monitor
        if(not os.path.isdir(path_to_data_now)):
            print("%s: No data available for this monitor " % monitor)
            continue
        output_folder = PATH_TO_PROCESS_DATA_STORAGE % monitor
        ensure_dir(output_folder)
        last_date_now = get_last_date_parsed(output_folder, monitor)
        if not last_date_now:
            parse_all_available_files_main()
            sys.exit()
        last_date_new = get_last_date_downloaded(path_to_data_now, monitor)
        if last_date_now.date() == last_date_new.date():
            print("\tNo new data to parse, exiting")
            continue
        print("\tOld: %s\n\tNew: %s" % (last_date_now.date(),
                                        last_date_new.date()))
        while(True):
            last_date_now += relativedelta(months=1)
            filename = "rib.%s.bz2" % last_date_now.strftime('%Y%m%d')
            raw_rib = os.path.join(path_to_data_now, filename)
            if os.path.isfile(raw_rib):
                dumped_rib = os.path.join(PATH_TO_TMP, filename[:-3] + "txt")
                command = command_for_mrt_dump_tool(dumped_rib, raw_rib)
                os.system(command)    
                feed_ases = extract_data_per_feeding_as(dumped_rib)
                print_route_server_data_to_file(feed_ases, last_date_now.year, 
                                                '%02d' % last_date_now.month,
                                                output_folder)
                print("%s: OK" % last_date_now.date())
            if last_date_now.date() == last_date_new.date():
                break

if __name__ == "__main__":
    # parse_all_available_files_main()
    incremental_parse_main()
