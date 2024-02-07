# changepersonmarkers
## Background
This code performs the analysis described in the following paper:

Peter Dekker, Sonja Gipper & Bart de Boer (2024). 3SG is the most conservative subject marker across languages. Accepted for Evolang 2024.


## Installation
With the script ``analyse_data.py``, an analysis of the rate of change of person markers for different grammatical persons is performed.

The script requires a few installation steps:
1. The script uses R, so install R, CMake and some dependencies needed for the R packages beforehand. On an Ubuntu machine:
```
sudo apt install r-base cmake libharfbuzz-dev libfribidi-dev
```

2. Install the Python package requirements:
```pip3 install -r requirements.txt``` (or with ``sudo`` for global install)

3. Install the required R packages:
```python3 install_r_pkgs.py``` (or with ``sudo`` for global install)

4. This script requires the file ``verbal_person-number_indexes_merged.csv`` from https://zenodo.org/records/7641119 to be in the folder ``data``.

5. Now you can run the script by running: ```python analyse_data.py```. It will output plots in the ``output_data`` directory. For the model using unnormalised Levenshtein distance, set the variable ``NORMALISATION`` to ``none``. For the normalised model, where the Levenshtein distance is divided by the length of the longest form, set ``NORMALISATION`` to ``max``.