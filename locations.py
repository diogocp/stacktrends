#!/usr/bin/env python3

import sqlite3

import geopy.geocoders


def main():
    con = sqlite3.connect("stackoverflow.sqlite")

    cursor = con.cursor()
    cursor.execute("SELECT DISTINCT Location FROM users")
    locations = list(zip(*cursor.fetchall()))[0]

    geocoders = [GoogleCountryCoder(),
                 NominatimCountryCoder()]

    coded_locations = []
    for location in locations:
        candidates = []
        for geocoder in geocoders:
            candidates.append(geocoder.getCountry(location))
        coded_locations.append(tuple([location] + [c for c in candidates]))

    print(coded_locations)

    with con:
        con.execute("DROP TABLE IF EXISTS locations")
        con.execute("CREATE TABLE locations(Location TEXT, Google TEXT, OSM TEXT)")
        con.executemany("""INSERT INTO locations(Location, Google, OSM)
                           VALUES (?, ?, ?)""", coded_locations)

    con.close()


class CountryCoder:
    def getCountry(self, location):
        raise NotImplementedError


class GoogleCountryCoder(CountryCoder):
    def __init__(self):
        self._geocoder = geopy.geocoders.GoogleV3()

    def getCountry(self, location):
        # TODO handle webservice errors
        response = self._geocoder.geocode(location)

        if response is None:
            return None

        for component in response.raw["address_components"]:
            if "country" in component["types"]:
                return component["short_name"]

        return None


class NominatimCountryCoder(CountryCoder):
    def __init__(self):
        self._geocoder = geopy.geocoders.Nominatim()

    def getCountry(self, location):
        # TODO handle webservice errors
        response = self._geocoder.geocode(location, addressdetails=True)

        if response is None:
            return None

        return response.raw["address"]["country_code"].upper()


if __name__ == "__main__":
    main()
