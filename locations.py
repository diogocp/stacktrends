#!/usr/bin/env python3

import sqlite3

import geopy.geocoders


def main():
    con = sqlite3.connect("stackoverflow.sqlite")

    cursor = con.cursor()
    cursor.execute("SELECT DISTINCT Location FROM users")
    locations = list(zip(*cursor.fetchall()))[0]

    tmpi = 0
    loc_country = list()
    for loc in locations:
        country_google = get_country_google(loc)
        country_osm = get_country_osm(loc)
        loc_country.append((loc, country_google, country_osm))

        tmpi = tmpi+1
        if tmpi > 20:
            break

    with con:
        con.execute("DROP TABLE IF EXISTS locations")
        con.execute("CREATE TABLE locations(Location TEXT, Google TEXT, OSM TEXT)")
        con.executemany("""INSERT INTO locations(Location, Google, OSM)
                           VALUES (?, ?, ?)""", loc_country)

    con.close()


def get_country_google(location):
    geolocator = geopy.geocoders.GoogleV3()

    # TODO handle webservice errors
    try:
        response = geolocator.geocode(location)
        for component in response.raw["address_components"]:
            if "country" in component["types"]:
                return component["short_name"]
    except Exception:
        pass

    return None


def get_country_osm(location):
    geolocator = geopy.geocoders.Nominatim()

    # TODO handle webservice errors
    try:
        response = geolocator.geocode(location)
        country = response.address.split(",")[-1].strip()
        return country
    except Exception:
        pass

    return None


if __name__ == "__main__":
    main()
