#!/usr/bin/env python3

from collections import Counter
import sqlite3

import geopy
from tqdm import tqdm


BING_API_KEY=""


def main():
    con = sqlite3.connect("stackoverflow.sqlite")

    cursor = con.cursor()
    cursor.execute("""SELECT DISTINCT TRIM(Location) AS Location
                      FROM users
                      WHERE Location != '' """)
    locations = list(zip(*cursor.fetchall()))[0]

    geocoders = [BingCountryCoder(BING_API_KEY),
                 GoogleCountryCoder(),
                 NominatimCountryCoder()]

    coded_locations = []
    for location in tqdm(locations):
        candidates = []
        for geocoder in geocoders:
            candidates.append(geocoder.getCountry(location))

        country = Counter(candidates).most_common(1)[0]
        if country[1] > len(candidates)/2:
            country = country[0]
        else:
            country = None

        coded_locations.append(tuple([location, country]
                                     + [c for c in candidates]))

    with con:
        con.execute("DROP TABLE IF EXISTS locations")
        con.execute("CREATE TABLE locations(Location TEXT, Country TEXT, Bing TEXT, Google TEXT, Nominatim TEXT)")
        con.executemany("""INSERT INTO locations(Location, Country, Bing, Google, Nominatim)
                           VALUES (?, ?, ?, ?, ?)""", coded_locations)

    con.close()


class CountryCoder:
    def getCountry(self, location):
        raise NotImplementedError


class BingCountryCoder(CountryCoder):
    def __init__(self, api_key):
        self._geocoder = geopy.geocoders.Bing(api_key, timeout=10)

    def getCountry(self, location):
        response = None
        try:
            response = self._geocoder.geocode(location,
                                              include_country_code=True)
        except geopy.exc.GeopyError as e:
            print("[Bing] '%s':" % location, e)

        if response is None:
            return None

        return response.raw["address"].get("countryRegionIso2")


class GoogleCountryCoder(CountryCoder):
    def __init__(self):
        self._geocoder = geopy.geocoders.GoogleV3(timeout=10)

    def getCountry(self, location):
        response = None
        try:
            response = self._geocoder.geocode(location)
        except geopy.exc.GeopyError as e:
            print("[Google] '%s':" % location, e)

        if response is None:
            return None

        for component in response.raw["address_components"]:
            if "country" in component["types"]:
                return component["short_name"]


class NominatimCountryCoder(CountryCoder):
    def __init__(self):
        self._geocoder = geopy.geocoders.Nominatim(timeout=10)

    def getCountry(self, location):
        response = None
        try:
            response = self._geocoder.geocode(location, addressdetails=True)
        except geopy.exc.GeopyError as e:
            print("[Nominatim] '%s':" % location, e)

        if response is None:
            return None

        return response.raw["address"]["country_code"].upper()


if __name__ == "__main__":
    main()
