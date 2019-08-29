"""
This script contains commands to BGP table dumps and communities from IX.br.

Commands were taken from Brito et al. (University of Campinas - UNICAMP)
This script is publicly available in:
https://github.com/intrig-unicamp/ixp-ptt-br/blob/master/raw_data/IXbr-RAW.sh
"""
path_to_data = "../../../../data/raw/lg"
path_to_location_files = "../../../../data/processed/peeringdb/ixbr"
# ixbr_locations_file = path_to_location_files + 'ixbr/' + 'peeringdb_ixbr_%s_%.2d_%.2d'
download_bgp_v4_aspaths = '(echo "term l 0"; sleep 1; echo "show ip bgp"; sleep 7m; echo "exit";) | telnet lg.%s.ptt.br | gzip -9 > %s/lg.%s.ptt.br_ipv4_bgp_routes_%s_%.2d_%.2d.txt.gz'
download_bgp_communities = '(echo "term l 0"; sleep 1; echo "show ip bgp community-info"; sleep 1m; echo "exit";) | telnet lg.%s.ptt.br | gzip -9 > %s/lg.%s.ptt.br_ipv4_bgp_communities_%s_%.2d_%.2d.txt.gz'
snapshot_name = 'lg.%s.ptt.br_ipv4_bgp_routes_%s_%.2d_%.2d.txt.gz'
path_to_process_data_storage = '../../../../data/processed/lg-ribs/v4'
path_to_tmp = '../../../../data/tmp'
stataring_date = '2018-06-01'
