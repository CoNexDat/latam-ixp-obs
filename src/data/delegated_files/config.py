"""
Thi is an example script.

It seems that it has to have THIS docstring with a summary line, a blank line
and sume more text like here. Wow.
"""
cmd_arin = 'wget https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-%s%.2d%.2d -O %s/arin/delegated-arin-extended-%s_%.2d_%.2d.txt'
cmd_ripe = 'wget https://ftp.ripe.net/pub/stats/ripencc/%s/delegated-ripencc-%s%.2d%.2d.bz2 -O %s/ripe/delegated-ripencc-extended-%s_%.2d_%.2d.txt.bz2'
cmd_apnic = 'wget https://ftp.apnic.net/stats/apnic/%s/delegated-apnic-%s%.2d%.2d.gz -O %s/apnic/delegated-apnic-extended-%s_%.2d_%.2d.txt.gz'
cmd_lacnic = 'wget https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-extended-%s%.2d%.2d -O %s/lacnic/delegated-lacnic-extended-%s_%.2d_%.2d.txt'
cmd_afrinic = 'wget https://ftp.afrinic.net/pub/stats/afrinic/%s/delegated-afrinic-%s%.2d%.2d -O %s/afrinic/delegated-afrinic-extended-%s_%.2d_%.2d.txt'
path_to_data_storage = '../../../data/raw/delegation_files'
path_to_process_data_storage = '../../../data/processed/delegation_files'
init_date = '2010-01-01'
rir_list = ['ripe', 'arin', 'lacnic', 'apnic', 'afrinic']
delegation_file_name_structure = 'delegated-%s-extended-%s_%.2d_%.2d.txt'
cmd_filter_prefixes_v4 = 'grep "ipv4" %s > %s'
cmd_filter_prefixes_v6 = 'grep "ipv6" %s > %s'
cmd_filter_ases = 'grep "asn" %s > %s'
path_to_tmp = '../../../data/tmp'
