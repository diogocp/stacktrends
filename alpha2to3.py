#!/usr/bin/env python3

import os

import pandas as pd
import pycountry


def main():
    os.chdir("data/out")

    for table in ["country_tag", "country_tag_month", "country_tag_year"]:
        df = pd.read_csv(table + ".csv", header=None)
        df[0] = df[0].map(lambda x: pycountry.countries.get(alpha_2=x).alpha_3)
        df.to_csv(table + ".csv", header=False, index=False)


if __name__ == "__main__":
    main()
