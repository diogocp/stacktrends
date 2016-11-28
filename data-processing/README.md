Stacktrends Data Processing
===========================


Dependencies
------------
To run these scripts, you will need to have Python 3 installed with SQLite and XML support.

The Python packages listed in `requirements.txt` must also be installed. This may be done automatically using the following command:
```sh
    pip install -r requirements.txt
```


Downloading the raw data
------------------------
The raw data can be obtained from the [Stack Exchange Data Dump](https://archive.org/details/stackexchange). The two tables used are (https://archive.org/download/stackexchange/stackoverflow.com-Posts.7z)[Posts] and (https://archive.org/download/stackexchange/stackoverflow.com-Users.7z)[Users]. Download them both and extract them to `data/raw/`.


Importing the raw data
----------------------
Run the script:
```sh
    python 1_import-so-data.py
```

This will import the relevant data from the XML files into an SQLite database in `data/stacktrends.sqlite`.


Geocoding locations
-------------------
Run the script:
```sh
    python 2_locations.py
```

Note: if you want to pipe stdout or if your terminal does not support Unicode, run the following command instead:
```sh
    PYTHONIOENCODING="utf-8" python 2_locations.py
```

This will create a new table `locations` in the SQLite database (`data/stacktrends.sqlite`) with the geocoded locations.


Creating the tidy data sets
---------------------------
Run the script:
```sh
    python 3_create-datasets.py
```

The data sets will be created in `data/`.
