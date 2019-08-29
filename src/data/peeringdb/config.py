"""
This script.

Author: Esteban Carisimo
Affiliaton: Universidad de Buenos Aires & CONICET
Year: 2016
Description:
    Small piece of code to find out which Netflix's OCAs are candadites for the
    the end-host that is running the code.
    The search of the OCAs is based on the information provided by fast.com
"""
peeringdb_url = 'https://www.peeringdb.com'
peeringdb_search_url = 'https://www.peeringdb.com/search?q=%s'
path_to_data = "../../../data/processed/peeringdb/"
cabase_output_dir = path_to_data + 'cabase/' + 'peeringdb_cabase_%s_%.2d_%.2d.csv'
ixbr_output_dir = path_to_data + 'ixbr/' + 'peeringdb_ixbr_%s_%.2d_%.2d.csv'
pitchile_output_dir = path_to_data + 'pitchile/' + 'peeringdb_pitchile_%s_%.2d_%.2d.csv'
