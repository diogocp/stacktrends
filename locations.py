#!/usr/bin/env python3

from collections import Counter
import configparser
import sqlite3

import geopy
from tqdm import tqdm


def main():
    config = configparser.ConfigParser()
    config.read("stacktrends.ini")

    con = sqlite3.connect(config["Database"]["filename"])
    cursor = con.cursor()
    cursor.execute("""SELECT DISTINCT Location FROM users
                      WHERE Location IS NOT NULL""")
    locations = list(zip(*cursor.fetchall()))[0]
    con.close()

    geocoders = [BingCountryCoder(config),
                 GoogleCountryCoder(config),
                 NominatimCountryCoder(config)]

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

    con = sqlite3.connect(config["Database"]["filename"])
    con.execute("DROP TABLE IF EXISTS locations")
    con.execute("CREATE TABLE locations(Location TEXT, Country TEXT, Bing TEXT, Google TEXT, Nominatim TEXT)")
    con.executemany("""INSERT INTO locations(Location, Country, Bing, Google, Nominatim)
                           VALUES (?, ?, ?, ?, ?)""", coded_locations)
    con.commit()
    con.close()


class CountryCoder:
    def getCountry(self, location):
        raise NotImplementedError


class BingCountryCoder(CountryCoder):
    def __init__(self, config):
        config = config["BingCountryCoder"]
        api_key = config["api_key"]
        timeout = float(config["timeout"])
        self._geocoder = geopy.geocoders.Bing(api_key, timeout=timeout)

    def getCountry(self, location):
        response = None
        try:
            response = self._geocoder.geocode(location,
                                              include_country_code=True)
        except geopy.exc.GeopyError as e:
            print("[Bing] '%s':" % location, e)

        try:
            return response.raw["address"]["countryRegionIso2"]
        except (AttributeError, KeyError):
            return None


class GoogleCountryCoder(CountryCoder):
    def __init__(self, config):
        config = config["GoogleCountryCoder"]
        timeout = float(config["timeout"])
        self._geocoder = geopy.geocoders.GoogleV3(timeout=timeout)

    def getCountry(self, location):
        response = None
        try:
            response = self._geocoder.geocode(location)
        except geopy.exc.GeopyError as e:
            print("[Google] '%s':" % location, e)

        try:
            for component in response.raw["address_components"]:
                if "country" in component.get("types", []):
                    return component["short_name"]
        except (AttributeError, KeyError):
            pass

        return None


class NominatimCountryCoder(CountryCoder):
    def __init__(self, config):
        config = config["NominatimCountryCoder"]
        timeout = float(config["timeout"])
        self._geocoder = geopy.geocoders.Nominatim(timeout=timeout)

    def getCountry(self, location):
        response = None
        try:
            response = self._geocoder.geocode(location, addressdetails=True)
        except geopy.exc.GeopyError as e:
            print("[Nominatim] '%s':" % location, e)

        try:
            return response.raw["address"]["country_code"].upper()
        except (AttributeError, KeyError):
            return None


if __name__ == "__main__":
    main()
