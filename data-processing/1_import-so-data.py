#!/usr/bin/env python3

import configparser
import sqlite3
from xml.etree import ElementTree


def main():
    config = configparser.ConfigParser()
    config.read("stacktrends.ini")

    con = sqlite3.connect(config["Database"]["filename"])

    import_table(con, "data/raw/Users.xml",
                 ("Id", "Location"),
                 ("INTEGER PRIMARY KEY", "TEXT"))
    import_table(con, "data/raw/Posts.xml",
                 ("Id", "PostTypeId", "ParentId", "CreationDate",
                  "OwnerUserId", "Tags"),
                 ("INTEGER PRIMARY KEY", "INTEGER", "INTEGER", "TEXT",
                  "INTEGER", "TEXT"))

    # Clean up users.Location
    con.execute("UPDATE users SET Location = TRIM(Location)")
    con.execute("UPDATE users SET Location = NULL WHERE Location = ''")
    con.commit()

    con.execute("VACUUM")
    con.close()


def import_table(con, filename, attribs, datatypes=None):
    if datatypes is None:
        colspec = attribs
    else:
        colspec = [" ".join(x) for x in zip(attribs, datatypes)]

    colspec = "(" + ", ".join(colspec) + ")"

    with open(filename, encoding="utf-8") as f:
        iterparser = ElementTree.iterparse(f, events=("start", "end"))
        _, root = next(iterparser)
        table = root.tag

        with con:
            con.execute("DROP TABLE IF EXISTS " + table)
            con.execute("CREATE TABLE IF NOT EXISTS " + table + colspec)

            for event, element in iterparser:
                if event == "end" and element.tag == "row":
                    con.execute("INSERT INTO " + table + " VALUES " +
                                "(" + ", ".join(["?"] * len(attribs)) + ")",
                                [element.get(x) for x in attribs])

                    # Don't keep rows in memory after processing them
                    root.clear()


if __name__ == "__main__":
    main()
