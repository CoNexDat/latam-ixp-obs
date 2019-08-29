"""
Defines global variables to use in download.py and parse.py

Defines all the variables to allow to download, parse and store RIBs downloaded
from RouteViews.
"""

DATA_SOURCE = 'rv'
IP_VERSION  = 'v4' 
# Generic URL where RVs stores all RIBs of all monitors
URL = "http://routeviews.org/route-views.%s/bgpdata/%s/RIBS/"
# Generic filename RVs uses to store all RIBs of all monitors
FILENAME_TO_DOWNLOAD = "rib.%s%s%s.%s.bz2"
# Paths where to store raw, processed and temporal data, respectively
PATH_TO_DATA_STORAGE = '../../../../data/raw/rv/v4/%s'
PATH_TO_PROCESS_DATA_STORAGE = '../../../../data/processed/ribs/v4/%s'
PATH_TO_TMP = '../../../../data/tmp'
# Monitors from which to download the RIBs
MONITORS = ["saopaulo"]
MONITORS_YEAR_OF_DEPLOY = {"saopaulo": "2011"}
# Initial and Final year of analysis
Y_I = 2011
Y_F = 2019
# Day in which the RIBs should be downloaded every month
DAY = "10"
# Usual hours to prioritize when looking for RIBs
HOURS_DUMP = ["%.4d" % i for i in range(0, 2400, 200)]
# MRT_DUMP_TOOL: choose between "bgpdump" and "bgpscanner"
MRT_DUMP_TOOL = "bgpdump"
# RIBs dump fields
if MRT_DUMP_TOOL == 'bgpdump':
    N_FIELDS_BGP_ENTRY  = 15    # Number of fields in BGP Snapshot Entry
    NEXT_HOP_FIELD      = 3     # Next Hop
    FEEDING_AS_FIELD    = 4     # AS that provides RIB
    PREFIX_FIELD        = 5     # Prefix
    AS_PATH_FIELD       = 6     # ASPath
elif MRT_DUMP_TOOL == 'bgpscanner':
    N_FIELDS_BGP_ENTRY   = 11  # Number of fields in BGP Snapshot Entry
    NH_AND_FEED_AS_FIELD = 8   # Both NH and FeedingAS
    NEXT_HOP_SUBFIELD    = 0   # Next Hop
    FEEDING_AS_SUBFIELD  = 1   # AS that provides RIB
    PREFIX_FIELD         = 1   # Prefix
    AS_PATH_FIELD        = 2   # ASPath
