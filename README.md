# mygardenia

This repository contains a wrapper to Gardenia that:
1. converts a custom TOML configuration file into Gardenia RGA and GAR files
2. calls the Gardenia executable using the generated RGA and GAR files
3. converts the Gardenia output time series into CSV files

Note: within the working directory, the structure must follow the example provided, 
i.e. three sub-directories *config*, *data*, and *output*.
