#!/usr/bin/env bash
# Change dir to where notebooks are
cd notebooks/v4/
# Look for every notebook in the repo; then rerun them
for nb in *.ipynb; do 
    jupyter nbconvert --ExecutePreprocessor.timeout=1200 --to notebook --execute $nb --output RERUN_$nb  
done