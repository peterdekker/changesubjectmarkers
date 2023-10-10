# Crosslinguistic analysis rate of change
With the script ``analyze_data.py``, an analysis of the rate of change of person markers for different grammatical persons is performed.

The script requires a few installation steps. The script uses R, so install R and CMake beforehand. On an Ubuntu machine:
```
sudo apt install r-base cmake
```
Install the Python package requirements:
```pip3 install -r requirements.txt``` (or with ``sudo`` for global install)

Install the required R packages:
```python3 install_r_pkgs.py``` (or with ``sudo`` for global install)

Now you can run the script with ```python analyze_data.py```. It will output plots in the ``output_data`` directory. This script requires the file ``verbal_person-number_indexes_merged.csv`` from https://zenodo.org/record/6028260 to be in the folder ``data``. 

## Calculation proportion persons in Corpus Gesproken Nederlands (CGN, Spoken Dutch Corpus)
analyze_cgn.py: Standalone script to count persons in Corpus Gesproken Nederlands (CGN, Spoken Dutch Corpus)
Download the annotations of the CGN corpus (full CGN corpus with sound files is not needed):

CGN-annotaties (Version 2.0.3) (2014) [Data set]. Available at the Dutch Language Institute: http://hdl.handle.net/10032/tm-a2-n5

The script expects the main 'Data' folder of the corpus to be placed in the directory 'data/CGNAnn'.