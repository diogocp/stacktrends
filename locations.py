#!/usr/bin/env python3

import sqlite3

from geopy.geocoders import GoogleV3


def main():
    con = sqlite3.connect("stackoverflow.sqlite")

    cursor = con.cursor()
    cursor.execute("SELECT Location FROM users GROUP BY Location")
    locations = list(zip(*cursor.fetchall()))[0]

    tmpi = 0
    loc_country = list()
    for loc in locations:
        country = get_country_google(loc)
        loc_country.append((loc, country))

        tmpi = tmpi+1
        if tmpi > 20:
            break

    with con:
        con.execute("DROP TABLE IF EXISTS locations")
        con.execute("CREATE TABLE locations(Location TEXT, Country TEXT)")
        con.executemany("""INSERT INTO locations(Location, Country)
                           VALUES (?, ?)""", loc_country)

    con.close()


def get_country_google(location):
    geolocator = GoogleV3()

    # TODO handle webservice errors
    try:
        response = geolocator.geocode(location)
        for component in response.raw["address_components"]:
            if "country" in component["types"]:
                return component["short_name"]
    except Exception:
        pass

    return None


if __name__ == "__main__":
    main()
