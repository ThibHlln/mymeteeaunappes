# mymeteaunappes

This repository contains utilities to facilitate contributions to 
MétéEau Nappes.

Note: within the working directory, the structure must follow the example provided, 
i.e. three sub-directories *config*, *data*, and *output*.

## myhubeau

This module contains functions that:
1. download hydrometric/piezometric/withdrawal data via Hub'Eau
2. save downloaded data as PRN files ready to use by Gardenia


## mycds

This module contains functions that:
1. download ERA5-land meteorological data via Copernicus' Climate Data Store (CDS)
2. save downloaded data as PRN files ready to use by Gardenia

## mygardenia

This module contains a wrapper to Gardenia that:
1. converts a custom TOML configuration file into Gardenia RGA and GAR files
2. calls the Gardenia executable using the generated RGA and GAR files
3. converts the Gardenia output time series into CSV files
