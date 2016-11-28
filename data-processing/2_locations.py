#!/usr/bin/env python3

from collections import Counter
import configparser
import sqlite3

import geopy
import pandas as pd
import pycountry
from tqdm import tqdm

# The ArcGIS geocoder in geopy does not return the country code,
# so we replace it with a modified local copy that does
import thirdparty.geopy.geocoders.arcgis
geopy.geocoders.ArcGIS = thirdparty.geopy.geocoders.arcgis.ArcGIS


def main():
    config = configparser.ConfigParser()
    config.read("stacktrends.ini")

    # Read distinct locations from the database
    con = sqlite3.connect(config["Database"]["filename"])
    locations = pd.read_sql_query("SELECT DISTINCT Location FROM users", con)
    locations = locations["Location"]
    con.close()

    # Drop locations that don't have any letters (most likely trash)
    locations.where(locations.str.contains("[^\W\d_]"), inplace=True)
    locations.dropna(inplace=True)

    # Set up geocoders
    # Google is disabled because it has a limit of 2500 queries per day
    geocoders = [ArcGISCountryCoder(config),
                 BingCountryCoder(config),
                 #GoogleCountryCoder(config),
                 NominatimCountryCoder(config)]

    # Main loop: for each location, query all the configured geocoders
    countries = pd.DataFrame(columns={"Location", "Country"})
    for location in tqdm(locations):
        candidate_countries = []
        for geocoder in geocoders:
            candidate_countries.append(geocoder.getCountry(location))

        # Store a country for this location only if there is a majority
        # of geocoders in agreement
        most_common_country = Counter(candidate_countries).most_common(1)[0]
        if most_common_country[1] > len(geocoders)/2:
            countries = countries.append({"Location": location,
                                          "Country": most_common_country[0]
                                         }, ignore_index=True)

    # Write the results to the SQLite database
    con = sqlite3.connect(config["Database"]["filename"])
    countries.to_sql("locations", con, if_exists="replace", index=False)
    con.close()


class CountryCoder:
    def getCountry(self, location):
        raise NotImplementedError


class ArcGISCountryCoder(CountryCoder):
    def __init__(self, config):
        config = config["ArcGISCountryCoder"]
        timeout = float(config.get("timeout", 10))
        self.retries = int(config.get("retries", 0))

        self._geocoder = geopy.geocoders.ArcGIS(timeout=timeout)

    def getCountry(self, location):
        response = None
        for attempt in range(self.retries + 1):
            try:
                response = self._geocoder.geocode(location)
                break
            except geopy.exc.GeocoderTimedOut as e:
                if attempt < self.retries:
                    continue
                else:
                    print("[ArcGIS] '%s':" % location, e)
                    break
            except geopy.exc.GeopyError as e:
                print("[ArcGIS] '%s':" % location, e)

        try:
            return response.raw["feature"]["attributes"]["Country"]
        except (AttributeError, KeyError):
            return None


class BingCountryCoder(CountryCoder):
    def __init__(self, config):
        config = config["BingCountryCoder"]
        api_key = config["api_key"]
        timeout = float(config.get("timeout", 10))
        self.retries = int(config.get("retries", 0))

        self._geocoder = geopy.geocoders.Bing(api_key, timeout=timeout)

    def getCountry(self, location):
        response = None
        for attempt in range(self.retries + 1):
            try:
                response = self._geocoder.geocode(location,
                                                  include_country_code=True)
                break
            except geopy.exc.GeocoderTimedOut as e:
                if attempt < self.retries:
                    continue
                else:
                    print("[Bing] '%s':" % location, e)
                    break
            except geopy.exc.GeopyError as e:
                print("[Bing] '%s':" % location, e)

        try:
            alpha2 = response.raw["address"]["countryRegionIso2"]
            return pycountry.countries.get(alpha_2=alpha2).alpha_3
        except (AttributeError, KeyError):
            return None


class GoogleCountryCoder(CountryCoder):
    def __init__(self, config):
        config = config["GoogleCountryCoder"]
        timeout = float(config.get("timeout", 10))
        self.retries = int(config.get("retries", 0))

        self._geocoder = geopy.geocoders.GoogleV3(timeout=timeout)

    def getCountry(self, location):
        response = None
        for attempt in range(self.retries + 1):
            try:
                response = self._geocoder.geocode(location)
                break
            except geopy.exc.GeocoderTimedOut as e:
                if attempt < self.retries:
                    continue
                else:
                    print("[Google] '%s':" % location, e)
                    break
            except geopy.exc.GeopyError as e:
                print("[Google] '%s':" % location, e)

        try:
            for component in response.raw["address_components"]:
                if "country" in component.get("types", []):
                    alpha2 = component["short_name"]
                    return pycountry.countries.get(alpha_2=alpha2).alpha_3
        except (AttributeError, KeyError):
            pass

        return None


class NominatimCountryCoder(CountryCoder):
    def __init__(self, config):
        config = config["NominatimCountryCoder"]
        timeout = float(config.get("timeout", 10))
        self.retries = int(config.get("retries", 0))

        self._geocoder = geopy.geocoders.Nominatim(timeout=timeout)

    def getCountry(self, location):
        response = None
        for attempt in range(self.retries + 1):
            try:
                response = self._geocoder.geocode(location,
                                                  addressdetails=True)
                break
            except geopy.exc.GeocoderTimedOut as e:
                if attempt < self.retries:
                    continue
                else:
                    print("[Nominatim] '%s':" % location, e)
                    break
            except geopy.exc.GeopyError as e:
                print("[Nominatim] '%s':" % location, e)

        try:
            alpha2 = response.raw["address"]["country_code"].upper()
            return pycountry.countries.get(alpha_2=alpha2).alpha_3
        except (AttributeError, KeyError):
            return None


if __name__ == "__main__":
    main()
