#!/usr/bin/env python3

import sqlite3
from xml.etree import ElementTree


def main():
    con = sqlite3.connect("stackoverflow.sqlite")

    import_table(con, "Tags.xml", ("TagName", "Count"))
    import_table(con, "Users.xml", ("AccountId", "Age", "Location"))
    import_table(con, "Posts.xml", ("CreationDate", "OwnerUserId", "Tags"))

    con.close()


def import_table(con, filename, attribs):
    with open(filename, encoding="utf-8") as f:
        iterparser = ElementTree.iterparse(f, events=("start", "end"))
        _, root = next(iterparser)

        table = root.tag
        colspec = "(" + ", ".join(attribs) + ")"

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
