#!/usr/bin/env python3

from collections import Counter
import configparser
import sqlite3

import geopy
import pandas as pd
import pycountry
from tqdm import tqdm

import thirdparty.geopy.geocoders.arcgis
geopy.geocoders.ArcGIS = thirdparty.geopy.geocoders.arcgis.ArcGIS


def main():
    config = configparser.ConfigParser()
    config.read("stacktrends.ini")

    # Read distinct locations from the database
    con = sqlite3.connect(config["Database"]["filename"])
    locations = pd.read_sql_query("SELECT DISTINCT Location FROM users", con)
    con.close()

    # Drop locations that don't have any letters
    locations = locations["Location"]
    locations.where(locations.str.contains("[^\W\d_]"), inplace=True)
    locations.dropna(inplace=True)

    # Set up geocoders
    geocoders = [ArcGISCountryCoder(config),
                 BingCountryCoder(config),
                 #GoogleCountryCoder(config),
                 NominatimCountryCoder(config)]

    countries = pd.DataFrame(columns={"Location", "Country"})
    for location in tqdm(locations):
        candidate_countries = []
        for geocoder in geocoders:
            candidate_countries.append(geocoder.getCountry(location))

        most_common_country = Counter(candidate_countries).most_common(1)[0]
        if most_common_country[1] > len(geocoders)/2:
            countries = countries.append({"Location": location,
                                          "Country": most_common_country[0]
                                         }, ignore_index=True)

    con = sqlite3.connect(config["Database"]["filename"])
    countries.to_sql("locations", con, if_exists="replace", index=False)
    con.close()


class CountryCoder:
    def getCountry(self, location):
        raise NotImplementedError


class ArcGISCountryCoder(CountryCoder):
    def __init__(self, config):
        config = config["ArcGISCountryCoder"]
        timeout = float(config["timeout"])
        self._geocoder = geopy.geocoders.ArcGIS(timeout=timeout)

    def getCountry(self, location):
        response = None
        try:
            response = self._geocoder.geocode(location)
        except geopy.exc.GeopyError as e:
            print("[ArcGIS] '%s':" % location, e)

        try:
            alpha3 = response.raw["feature"]["attributes"]["Country"]
            return pycountry.countries.get(alpha3=alpha3).alpha2
        except (AttributeError, KeyError):
            return None


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
