#!/usr/bin/env bash
#################################################################
# Crawl PeeringDB to get IXP names in Argentina, Brazil and Chile
#################################################################
# Change Dir to where crawling files are
cd src/data/peeringdb/
# Get IXP names from CABASE (Argentina)
python get_cabase.py
# Get IXP names from IX.br (Brazil)
python get_ixbr.py
# Get IXP names from PIT Chile (Brazil)
python get_pitchile.py
# Get back to repo root dir
cd ../../../
#################################################################
# Download PCH files
#################################################################
# Change Dir to where PCH files are
cd src/data/pch/v4/
# Download PCH table dumps
python download.py
# Parse data
python parse.py
# Get back to repo root dir
cd ../../../../
#################################################################
# Download RouteViews files
#################################################################
# Change Dir to where RV files are
cd src/data/rv/v4/
# Download RV table dumps
python download.py
# Parse data
python parse.py
# Get back to repo root dir
cd ../../../../
#################################################################
# Dump current BGP tables from IX.br Looking glasses
#################################################################
# Change Dir to where LG files are
cd src/data/lg/v4/
# Download LG table dumps
python download.py
# Parse data
python parse.py
# Get back to repo root dir
cd ../../../../
#################################################################
# Download CAIDA’s AS-REL files
#################################################################
# Change Dir to where CAIDA’s AS-REL files are
cd src/data/asrel/
# Download CAIDA’s AS-REL files
python download.py
# Get back to repo root dir
cd ../../../
#################################################################
# Download RIR delegation files
#################################################################
# Change Dir to where RIR delegation files are
cd src/data/delegated_files/
# Download RIR delegation files
python download.py
# Parse data
python parse.py
# Get back to repo root dir
cd ../../../
#################################################################
# Download CAIDA’s prefix-to-AS files
#################################################################
# Change Dir to where CAIDA’s prefix-to-AS files are
cd src/data/pfix2as/v4/
# Download CAIDA’s prefix-to-AS table dumps
python download.py
# Get back to repo root dir
cd ../../../../
#################################################################
# Compute origin address space in LACNIC region
#################################################################
# Change Dir to where RV files are
cd src/data/origin_addr_space/
# Compute
python compute_orgin_addr_space.py
# Get back to repo root dir
cd ../../../
